
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix, classification_report

def train_binary_classifier(df, target, model_name="Logistic Regression", test_size=0.25, random_state=42):
    if target not in df:
        raise ValueError("Selected outcome field does not exist.")
    work=df.copy()
    work=work.dropna(subset=[target])
    y=work[target].astype(str)
    classes=y.unique()
    if len(classes)!=2:
        raise ValueError(f"Binary outcome required; selected field has {len(classes)} classes.")
    if len(work)<50:
        raise ValueError("At least 50 labelled records are required for this demonstration.")
    counts=y.value_counts()
    if counts.min()<10:
        raise ValueError("Each outcome class must have at least 10 records.")
    X=work.drop(columns=[target])
    # Exclude likely identifiers and free-text fields to reduce leakage/noise.
    drop_cols=[c for c in X.columns if any(k in str(c).lower() for k in ["customer id","account id","record id","name","email","phone"])]
    X=X.drop(columns=drop_cols,errors="ignore")
    if X.empty:
        raise ValueError("No usable predictor fields remain after excluding identifiers.")
    numeric_cols=X.select_dtypes(include=np.number).columns.tolist()
    categorical_cols=[c for c in X.columns if c not in numeric_cols]
    numeric_pipe=Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical_pipe=Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))])
    transformers=[]
    if numeric_cols: transformers.append(("num",numeric_pipe,numeric_cols))
    if categorical_cols: transformers.append(("cat",categorical_pipe,categorical_cols))
    prep=ColumnTransformer(transformers)
    model=LogisticRegression(max_iter=1500,class_weight="balanced") if model_name=="Logistic Regression" else RandomForestClassifier(n_estimators=250,min_samples_leaf=3,class_weight="balanced",random_state=random_state)
    pipeline=Pipeline([("preprocess",prep),("model",model)])
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=test_size,random_state=random_state,stratify=y)
    pipeline.fit(X_train,y_train)
    pred=pipeline.predict(X_test)
    proba=pipeline.predict_proba(X_test)[:,1]
    positive_class=pipeline.classes_[1]
    try: auc=roc_auc_score((y_test==positive_class).astype(int),proba)
    except: auc=np.nan
    metrics={
        "Accuracy":accuracy_score(y_test,pred),
        "Precision (positive class)":precision_score(y_test,pred,pos_label=positive_class,zero_division=0),
        "Recall (positive class)":recall_score(y_test,pred,pos_label=positive_class,zero_division=0),
        "ROC-AUC":auc,
        "Training records":len(X_train),
        "Test records":len(X_test),
        "Positive class":positive_class,
    }
    cm=confusion_matrix(y_test,pred,labels=pipeline.classes_)
    cm_df=pd.DataFrame(cm,index=[f"Actual {x}" for x in pipeline.classes_],columns=[f"Predicted {x}" for x in pipeline.classes_])
    return pipeline, metrics, cm_df, classification_report(y_test,pred,zero_division=0)
