#/bin/bash
# script per generare il file delle iscrizioni scolastiche per Archimede 26

set -e
set -u

export OLI_EDITION=olimat26
CONTEST_ID=27 # contest febbraio 2026

echo "OLI_EDITION=${OLI_EDITION}"
echo "CONTEST_ID=${CONTEST_ID}"
echo "(per elencare i contest esegui: python contests.py)"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
SCUOLE="${TIMESTAMP}_schools_2026.csv"
SEDI="${TIMESTAMP}_venues_2026.csv"
OUT="${TIMESTAMP}_olifogli_2026.csv"

# scarica elenco scuole iscritte
if [ -f "${SCUOLE}" ]; then
    echo "File ${SCUOLE} già esistente. Rimuovilo se vuoi rigenerarlo."
    exit 1
else
    python school_subscriptions.py olimat26 > "${SCUOLE}".partial
    mv "${SCUOLE}".partial "${SCUOLE}"
    echo "File generato: ${SCUOLE}"
fi

# scarica elenco sedi di gara
if [ -f "${SEDI}" ]; then
    echo "File ${SEDI} già esistente. Rimuovilo se vuoi rigenerarlo."
    exit 1
else
    python venues.py 27 > "${SEDI}".partial
    mv "${SEDI}".partial "${SEDI}"
    wc --lines "${SEDI}"
    echo "File generato: ${SEDI}"
fi

# unisce i due file
python merge_schools_coordinators.py "${SCUOLE}" "${SEDI}" > "${OUT}".partial
mv "${OUT}".partial "${OUT}"
echo "File generato: ${OUT}"
