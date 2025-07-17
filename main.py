#!/usr/bin/env python3
"""
Azure DevOps AI Assistant
========================

Um assistente inteligente para interagir com Azure DevOps
através de chat natural com interface gráfica desktop.

Desenvolvido com Python e Tkinter.
"""

import sys
import os
import traceback
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app_controller import AppController
from src.utils.logger import logger

def setup_environment():
    """Setup application environment"""
    try:
        # Create necessary directories
        directories = [
            "config",
            "logs",
            "data",
            "exports"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        # Set up logging
        logger.info("Environment setup completed")
        
    except Exception as e:
        print(f"Error setting up environment: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import tkinter
        import requests
        import yaml
        import dotenv
        
        # Check optional dependencies
        optional_deps = {
            'openai': 'OpenAI API support',
            'anthropic': 'Anthropic Claude support',
            'google.generativeai': 'Google Gemini support'
        }
        
        missing_optional = []
        for module, description in optional_deps.items():
            try:
                __import__(module)
            except ImportError:
                missing_optional.append(f"{module} ({description})")
        
        if missing_optional:
            logger.warning(f"Missing optional dependencies: {', '.join(missing_optional)}")
            logger.warning("Some LLM providers may not be available")
        
        logger.info("Dependencies check completed")
        
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install required dependencies with: pip install -r requirements.txt")
        sys.exit(1)

def show_startup_banner():
    """Show application startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Azure DevOps AI Assistant                 ║
║                                                              ║
║  🤖 Assistente inteligente para Azure DevOps                ║
║  💬 Chat natural com interface gráfica                      ║
║  📋 Visualização de boards e work items                     ║
║  🔍 Busca inteligente de itens                             ║
║                                                              ║
║  Versão: 1.0.0                                              ║
║  Desenvolvido com Python e Tkinter                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def show_error_and_exit(error_message: str, details: str = ""):
    """Show error message and exit"""
    print("\n" + "="*60)
    print("❌ ERRO NA APLICAÇÃO")
    print("="*60)
    print(f"Erro: {error_message}")
    if details:
        print(f"\nDetalhes: {details}")
    print("\nPara suporte, verifique:")
    print("• Configuração do arquivo .env")
    print("• Configuração do arquivo config/app_config.yaml")
    print("• Logs em logs/app.log")
    print("="*60)
    sys.exit(1)

def main():
    """Main application entry point"""
    try:
        # Show startup banner
        show_startup_banner()
        
        # Setup environment
        print("🔧 Configurando ambiente...")
        setup_environment()
        
        # Check dependencies
        print("📦 Verificando dependências...")
        check_dependencies()
        
        # Create and run application
        print("🚀 Iniciando aplicação...")
        app_controller = AppController()
        app_controller.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Aplicação interrompida pelo usuário")
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        error_message = str(e)
        details = traceback.format_exc()
        
        logger.error(f"Application error: {error_message}")
        logger.error(f"Traceback: {details}")
        
        show_error_and_exit(error_message, details)

if __name__ == "__main__":
    main() 