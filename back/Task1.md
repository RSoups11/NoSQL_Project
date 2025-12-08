# Tache 1 (Windows) : 

## Démarrer MongoDB (Windows)

    Ouvrir PowerShell en administrateur si besoin :

    Get-Service -Name MongoDB
    Start-Service -Name MongoDB
    Get-Service -Name MongoDB

    Attendu :
    Status = Running

## Lancer l’API FastAPI

    Ouvrir un terminal normal :

    cd C:\Users\amrou\NoSQL_Project\back
    uvicorn main:app --reload

    Attendu :

    Uvicorn running on http://127.0.0.1:8000

    Application startup complete

    Laisser ce terminal ouvert.

## Tester le peuplement en UNE seule requête

    Ouvrir un 2e terminal PowerShell (normal).

    IMPORTANT :
    Sous PowerShell, utiliser Invoke-RestMethod
    (car "curl -X" peut échouer).

    Commande :

    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/task1/load
    "

    OU (si l’endpoint existe) :

    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/task1/load/data_sample.tsv
    "

    Attendu :
    Un JSON avec un message OK et un nombre "inserted" > 0.

