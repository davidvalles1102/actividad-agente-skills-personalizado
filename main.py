"""CLI del sistema agentico refactorizado.

Uso:
    python main.py --agent ada_productividad
    python main.py --agent rex_tecnico

Carga un AgentConfig (agents/*.json), descubre las skills disponibles en
skills/ y arranca un loop de conversacion por terminal. Este archivo solo
conecta piezas: no contiene logica de negocio (esa vive en core/ y en
cada skill), a diferencia de legacy/agente_monolitico.py.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from core.agent import Agent
from core.config import AgentConfig
from core.skill_registry import discover

BASE_DIR = Path(__file__).resolve().parent
AGENTS_DIR = BASE_DIR / "agents"
SKILLS_DIR = BASE_DIR / "skills"
DATA_DIR = BASE_DIR / "data"


def _load_dotenv(path: Path) -> None:
    """Carga variables tipo .env sin depender de python-dotenv (ver requirements.txt)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if value:
            os.environ.setdefault(key, value)


def build_agent(agent_id: str) -> Agent:
    config_path = AGENTS_DIR / f"{agent_id}.json"
    if not config_path.exists():
        disponibles = ", ".join(p.stem for p in AGENTS_DIR.glob("*.json"))
        raise SystemExit(f"Agente '{agent_id}' no encontrado. Disponibles: {disponibles}")

    config = AgentConfig.load(config_path)
    skills = discover(SKILLS_DIR)
    return Agent(config=config, skills=skills, data_dir=DATA_DIR)


def run_cli(agent_id: str) -> None:
    agent = build_agent(agent_id)
    print(f"== {agent.config.name} ({agent.config.role}) ==")
    print("Escribe 'salir' para terminar, o 'skills' para ver las capacidades disponibles.\n")

    while True:
        try:
            message = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not message:
            continue
        if message.lower() in {"salir", "exit", "quit"}:
            break
        if message.lower() == "skills":
            for name, skill in agent.skills.items():
                print(f"- {name}: {skill.description}")
            print()
            continue

        response = agent.handle_message(message)
        print(f"{agent.config.name} [{response.source}]: {response.text}\n")


def main() -> None:
    _load_dotenv(BASE_DIR / ".env")

    parser = argparse.ArgumentParser(description="CLI del sistema agentico con skills propias.")
    parser.add_argument(
        "--agent",
        default="ada_productividad",
        help="Id del agente a cargar (nombre del archivo json en agents/, sin extension).",
    )
    args = parser.parse_args()
    run_cli(args.agent)


if __name__ == "__main__":
    main()
