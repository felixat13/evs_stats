# 📊 Explorateur EVS/WVS 2017-2022

Interface interactive et facile d'utilisation pour explorer le dataset EVS (European Values Study) et WVS (World Values Survey) sans avoir besoin de compétences techniques.

![Application Screenshot](https://via.placeholder.com/800x400?text=Application+Streamlit+EVS)

---

## 🎯 Fonctionnalités

✅ **Filtrage facile** : Par pays, année, et autres critères  
✅ **Visualisations interactives** : Graphiques, distributions, comparaisons  
✅ **Comparaisons entre pays** : Identifiez les tendances culturelles  
✅ **Croisement de variables** : Explorez les corrélations  
✅ **Export des données** : Téléchargez vos résultats filtrés  
✅ **Interface intuitive** : Aucune compétence technique requise  

---

## 🚀 Installation rapide (3 minutes)

### Étape 1 : Installer Python
Téléchargez et installez Python depuis https://www.python.org/downloads/  
⚠️ **Important** : Cochez "Add Python to PATH" lors de l'installation

### Étape 2 : Installer les dépendances
Ouvrez un terminal dans ce dossier et tapez :
```bash
pip install -r requirements.txt
```

### Étape 3 : Lancer l'application

#### Sur Windows :
Double-cliquez sur `lancer_application.bat`

#### Sur Mac/Linux :
```bash
./lancer_application.sh
```

#### Méthode universelle :
```bash
streamlit run evs_streamlit_app.py
```

L'application s'ouvrira automatiquement dans votre navigateur ! 🎉

---

## 📁 Structure des fichiers

```
Explorateur_EVS/
│
├── data_evs_mapped.csv          # Vos données (à placer ici)
│
├── evs_streamlit_app.py         # Application Streamlit (recommandé)
├── evs_explorer.py              # Application Marimo (alternative)
│
├── requirements.txt             # Liste des dépendances Python
├── GUIDE_UTILISATION.md         # Guide détaillé en français
├── README.md                    # Ce fichier
│
├── lancer_application.bat       # Script de lancement Windows
└── lancer_application.sh        # Script de lancement Mac/Linux
```

---

## 📖 Guide d'utilisation

### Interface principale

L'application Streamlit est divisée en plusieurs sections :

#### 1. Configuration (barre latérale)
- Vérifiez le chemin du fichier CSV
- Choisissez entre échantillon (rapide) ou dataset complet

#### 2. Filtres
- **Pays** : Sélectionnez un ou tous les pays
- **Année** : Filtrez par année d'enquête (2017-2022)

#### 3. Analyse d'une variable
- Choisissez une catégorie (Vie personnelle, Bien-être, Politique, etc.)
- Sélectionnez une variable
- Visualisez la distribution et les statistiques

#### 4. Comparaison entre pays
- Comparez une variable entre différents pays
- Top N pays selon la variable choisie

#### 5. Croisement de variables
- Explorez les relations entre deux variables
- Visualisez les corrélations

#### 6. Export
- Téléchargez les données filtrées en CSV

---

## 💡 Exemples d'utilisation

### Exemple 1 : Comparer le bonheur entre pays
1. Dans "Comparaison entre pays"
2. Sélectionnez "Feeling of happiness"
3. Ajustez le nombre de pays à 20
4. Identifiez les pays les plus heureux !

### Exemple 2 : Explorer la confiance en France
1. Filtrez par pays : France
2. Dans "Analyse d'une variable"
3. Catégorie : "Confiance et société"
4. Variable : "Most people can be trusted"
5. Observez la distribution

### Exemple 3 : Relation bonheur et politique
1. Dans "Croisement de variables"
2. Variable X : "Satisfaction with your life"
3. Variable Y : "Interest in politics"
4. Analysez la corrélation

---

## 🎓 À propos des données

### Dataset EVS/WVS 2017-2022

- **Sources** : European Values Study (EVS) 2017 + World Values Survey (WVS) Wave 7
- **Taille** : ~157 000 réponses
- **Pays** : Dizaines de pays à travers le monde
- **Variables** : 231 variables couvrant :
  - Valeurs personnelles (famille, travail, religion)
  - Bien-être et bonheur
  - Confiance sociale
  - Politique et démocratie
  - Attitudes sociales

### Échelles de réponse

- **1-4** : Échelles d'accord (Très important → Pas du tout important)
- **1-10** : Échelles de satisfaction
- **0-1** : Variables binaires (Non → Oui)

---

## 🔧 Résolution de problèmes

### Problème : "Module not found"
**Solution** : Réinstallez les dépendances
```bash
pip install -r requirements.txt
```

### Problème : "File not found"
**Solution** : Vérifiez que `data_evs_mapped.csv` est dans le même dossier

### Problème : L'application est lente
**Solution** : Utilisez l'échantillon de données (option dans la barre latérale)

### Problème : Le navigateur ne s'ouvre pas
**Solution** : Copiez l'URL affichée dans le terminal (http://localhost:8501)

---

## 🌟 Alternatives

### Streamlit (Recommandé)
- **Fichier** : `evs_streamlit_app.py`
- **Avantage** : Interface très intuitive, idéale pour les non-techniciens
- **Lancement** : `streamlit run evs_streamlit_app.py`

### Marimo
- **Fichier** : `evs_explorer.py`
- **Avantage** : Notebook interactif, bon pour l'exploration
- **Lancement** : `marimo edit evs_explorer.py`

---

## 🤝 Contribution

Des suggestions pour améliorer l'application ? 
- Ajoutez de nouvelles visualisations
- Proposez de nouvelles fonctionnalités
- Signalez des bugs

---

## 📚 Ressources

- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation Pandas](https://pandas.pydata.org/docs/)
- [EVS Website](https://europeanvaluesstudy.eu/)
- [WVS Website](https://www.worldvaluessurvey.org/)

---

## 📄 Licence

Les données EVS/WVS sont soumises à leurs propres licences. Consultez les sites officiels pour plus d'informations.

---

## ⭐ Support

Si vous trouvez cet outil utile, n'hésitez pas à le partager avec vos collègues !

**Créé avec ❤️ pour faciliter l'exploration des données EVS/WVS**

---

**Version** : 1.0  
**Dernière mise à jour** : Janvier 2026
