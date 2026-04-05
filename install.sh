#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
SKILLS_DST="$HOME/.claude/skills"

echo "=== atdd-orchestrator install ==="
echo ""

# ── 1. Sincronizar skills ────────────────────────────────────────────────────
echo "[1/2] Sincronizando skills → $SKILLS_DST"

for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name="$(basename "$skill_dir")"
    dst="$SKILLS_DST/$skill_name"

    rm -rf "$dst"
    cp -r "$skill_dir" "$dst"
    echo "      ✓ $skill_name"
done

# ── 2. Instalar dependencias Python ─────────────────────────────────────────
echo ""
echo "[2/2] Instalando dependencias Python"

if [[ ! -d "$REPO_DIR/.venv" ]]; then
    python3 -m venv "$REPO_DIR/.venv"
fi

"$REPO_DIR/.venv/bin/pip" install -e "$REPO_DIR" -q
echo "      ✓ atdd-orchestrator instalado en .venv"

echo ""
echo "=== Instalación completa ==="
echo ""
echo "Antes de iniciar:"
echo "  cp .env.example .env          # y configurar las variables"
echo "  cp projects.yml.example projects.yml  # y agregar tus proyectos"
echo ""
echo "Para iniciar el orquestador (servidor remoto):"
echo "  docker compose up -d --build"
echo ""
echo "Servicios que levanta:"
echo "  redis          — broker de colas"
echo "  git-sync       — polling, detecta inbox, commit+push"
echo "  test-engineer  — cola: inbox"
echo "  developer      — cola: ready-to-dev"
echo "  tester         — cola: ready-to-test"
echo "  atf-worker     — cola: ready-to-atf"
