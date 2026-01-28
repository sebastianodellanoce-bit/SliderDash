#!/bin/bash
# Script Bash per build e push su Docker Hub
# Esegui questo script dalla cartella del progetto

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🐳 Docker Hub Deployment Script${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Verifica parametri
if [ -z "$1" ]; then
    echo -e "${RED}❌ Errore: Specifica il tuo Docker Hub username${NC}"
    echo "Uso: ./deploy-to-dockerhub.sh <username> [image-name] [tag]"
    echo "Esempio: ./deploy-to-dockerhub.sh mionome enpal-streamlit latest"
    exit 1
fi

DOCKER_HUB_USERNAME=$1
IMAGE_NAME=${2:-"enpal-streamlit"}
TAG=${3:-"latest"}
FULL_IMAGE_NAME="$DOCKER_HUB_USERNAME/$IMAGE_NAME:$TAG"

# Verifica che Docker sia installato
echo -e "${YELLOW}1. Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}   ❌ Docker non trovato! Installa Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Docker trovato: $(docker --version)${NC}"

# Verifica che Docker sia in esecuzione
echo -e "${YELLOW}2. Verificando che Docker sia in esecuzione...${NC}"
if ! docker ps &> /dev/null; then
    echo -e "${RED}   ❌ Docker non è in esecuzione! Avvia Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Docker è in esecuzione${NC}"

# Login a Docker Hub
echo -e "${YELLOW}3. Login a Docker Hub...${NC}"
echo "   Inserisci la tua password Docker Hub quando richiesto"
docker login -u $DOCKER_HUB_USERNAME
if [ $? -ne 0 ]; then
    echo -e "${RED}   ❌ Login fallito!${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Login riuscito${NC}"

# Build dell'immagine
echo -e "${YELLOW}4. Building immagine: $FULL_IMAGE_NAME${NC}"
echo "   Questo potrebbe richiedere 5-10 minuti..."
docker build -t $FULL_IMAGE_NAME .
if [ $? -ne 0 ]; then
    echo -e "${RED}   ❌ Build fallita!${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Build completata${NC}"

# Push dell'immagine
echo -e "${YELLOW}5. Pushing immagine su Docker Hub...${NC}"
echo "   Questo potrebbe richiedere 5-15 minuti..."
docker push $FULL_IMAGE_NAME
if [ $? -ne 0 ]; then
    echo -e "${RED}   ❌ Push fallito!${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Push completato${NC}"

echo ""
echo -e "${GREEN}🎉 Completato!${NC}"
echo ""
echo -e "${CYAN}Immagine disponibile su Docker Hub:${NC}"
echo -e "   ${FULL_IMAGE_NAME}"
echo ""
echo -e "${CYAN}Ora puoi usare questa immagine in Azure Container App:${NC}"
echo -e "   - Origine: Docker Hub o altri registri"
echo -e "   - Immagine: $DOCKER_HUB_USERNAME/$IMAGE_NAME"
echo -e "   - Tag: $TAG"
echo ""

