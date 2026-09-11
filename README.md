# CardioVeyra
## An Intelligent Machine Learning Framework for Heart Disease Prediction

### Final project package
This package contains the Django application, dataset, trained model artifacts, evaluation metrics/charts, source code, and complete project documentation.

### Run on Windows
```text
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
python manage.py runserver
```
Open `http://127.0.0.1:8000/`.

### Final methodology
- Dataset records: 303
- Predictor features: 13
- Train/test split: 80% / 20%
- Random state: 0
- KNN: 7 neighbors
- SVM: linear kernel
- Random Forest: 100 estimators
- Final application model: Random Forest

### Theme
Use the **Dark / Light** button in the top navigation. The selected theme is remembered in the browser.

### Documentation
- `CardioVeyra_Project_Documentation.docx`
- `CardioVeyra_Project_Documentation.pdf`

### Important
This is an academic prediction system. It is not a certified diagnostic tool and model probability is not a medically validated probability.
