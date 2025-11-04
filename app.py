import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

st.title("Iris 꽃 분류기 🌸")

iris = load_iris()
X, y = iris.data, iris.target

clf = RandomForestClassifier()
clf.fit(X, y)

sepal_length = st.slider("Sepal length", 4.0, 8.0, 5.0)
sepal_width = st.slider("Sepal width", 2.0, 4.5, 3.0)
petal_length = st.slider("Petal length", 1.0, 7.0, 4.0)
petal_width = st.slider("Petal width", 0.1, 2.5, 1.0)

sample = [[sepal_length, sepal_width, petal_length, petal_width]]
prediction = clf.predict(sample)
predicted_class = iris.target_names[prediction[0]]

st.write(f"🌺 예측된 품종: **{predicted_class}**")
