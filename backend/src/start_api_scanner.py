"""
Iniciar API do Bot com Scanner Automático
"""
import sys
import os

print("🚀 Iniciando API do Bot de Trading com Scanner...\n")
print("📊 O scanner vai monitorar 160+ moedas automaticamente!")
print("🔍 Análise a cada 60 segundos")
print("📈 Pontuação de 0-5 para cada ativo")
print("\n⏳ Iniciando servidor...\n")

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(root_dir)
os.system(f'start cmd /k "cd /d {root_dir} && set PYTHONPATH=backend\\src && set PYTHONIOENCODING=utf-8 && uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"')

print("\n✅ API iniciando em nova janela!")
print("\n📱 Acesse:")
print("   🌐 API Docs: http://localhost:8000/docs")
print("   📊 Scanner: http://localhost:8000/scanner/results")
print("   📈 Monitor Web: Abrir src/monitor_web")
print("\n💡 O scanner já está rodando em background!")
