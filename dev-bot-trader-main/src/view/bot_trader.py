import streamlit as st
import time
import psutil
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from managers.trading_process_manager import TradingProcessManager
from utils.default_strategies import DEFAULT_STRATEGIES

def main():
    st.set_page_config(
        page_title="Trading Bot Dashboard",
        page_icon="��",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Dashboard de Trading Bots")
    st.markdown("---")
    
    # Inicializar gerenciador de processos
    if 'process_manager' not in st.session_state:
        st.session_state.process_manager = TradingProcessManager()
    
    manager = st.session_state.process_manager
    
    # Sidebar para adicionar novas estratégias
    with st.sidebar:
        st.header("➕ Adicionar Nova Estratégia")
        
        strategy_type = st.selectbox(
            "Tipo de Estratégia",
            list(DEFAULT_STRATEGIES.keys()),
            format_func=lambda x: DEFAULT_STRATEGIES[x]['name']
        )
        
        if strategy_type:
            strategy_info = DEFAULT_STRATEGIES[strategy_type]
            st.subheader(strategy_info['name'])
            st.caption(strategy_info['description'])
            
            # Configurações da estratégia
            st.subheader("Configurações")
            
            config = {}
            for key, default_value in strategy_info['default_config'].items():
                if isinstance(default_value, int):
                    config[key] = st.number_input(key, value=default_value, key=f"config_{key}")
                elif isinstance(default_value, float):
                    config[key] = st.number_input(key, value=default_value, key=f"config_{key}")
                else:
                    config[key] = st.text_input(key, value=default_value, key=f"config_{key}")
            
            if st.button("🚀 Iniciar Estratégia", type="primary"):
                # Converter configurações para argumentos
                args = []
                for key, value in config.items():
                    args.extend([f'--{key}', str(value)])
                
                process_id = manager.start_process(
                    strategy_info['name'],
                    strategy_info['script'],
                    args,
                    config
                )
                
                st.success(f"Estratégia iniciada com PID: {process_id}")
                st.rerun()
    
    # Área principal - Lista de processos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Processos Ativos")
        
        if not manager.processes:
            st.info("Nenhum processo ativo. Adicione uma estratégia na sidebar.")
        else:
            for process_id, process_info in manager.processes.items():
                with st.container():
                    st.markdown("---")
                    
                    # Status do processo
                    current_status = manager.get_process_status(process_id)
                    
                    col_status, col_actions = st.columns([3, 1])
                    
                    with col_status:
                        status_color = "🟢" if current_status == 'running' else "🔴"
                        st.markdown(f"**{status_color} PID: {process_id}**")
                        st.markdown(f"**Estratégia:** {process_info['strategy_name']}")
                        
                        # Mostrar configurações
                        if process_info.get('config'):
                            config_text = ", ".join([f"{k}: {v}" for k, v in process_info['config'].items()])
                            st.caption(f"Config: {config_text}")
                        
                        # Tempo de execução
                        if 'start_time' in process_info:
                            start_time = datetime.fromisoformat(process_info['start_time'])
                            runtime = datetime.now() - start_time
                            st.caption(f"Executando há: {str(runtime).split('.')[0]}")
                    
                    with col_actions:
                        if current_status == 'running':
                            if st.button("⏸️ Pausar", key=f"stop_{process_id}"):
                                if manager.stop_process(process_id):
                                    st.success("Processo parado!")
                                    st.rerun()
                        else:
                            if st.button("▶️ Reiniciar", key=f"restart_{process_id}"):
                                new_pid = manager.restart_process(process_id)
                                if new_pid:
                                    st.success(f"Processo reiniciado! Novo PID: {new_pid}")
                                    st.rerun()
                        
                        if st.button("🗑️ Remover", key=f"remove_{process_id}"):
                            manager.stop_process(process_id)
                            del manager.processes[process_id]
                            if process_id in manager.process_logs:
                                del manager.process_logs[process_id]
                            manager.save_config()
                            st.success("Processo removido!")
                            st.rerun()
    
    with col2:
        st.header("📈 Estatísticas")
        
        if manager.processes:
            try:
                running_count = sum(1 for pid in manager.processes.keys() if manager.get_process_status(pid) == 'running')
                
                st.metric("Processos Ativos", running_count)
                st.metric("Total de Processos", len(manager.processes))
            except Exception as e:
                st.error(f"Erro ao calcular estatísticas: {e}")
            
            # Uso de CPU e memória
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                st.subheader("Sistema")
                st.metric("CPU", f"{cpu_percent:.1f}%")
                st.metric("Memória", f"{memory.percent:.1f}%")
            except Exception as e:
                st.error(f"Erro ao obter estatísticas do sistema: {e}")
    
    # Área de logs
    st.header("📝 Logs em Tempo Real")
    
    if manager.processes:
        try:
            selected_process = st.selectbox(
                "Selecionar processo para ver logs:",
                list(manager.processes.keys()),
                format_func=lambda x: f"PID {x} - {manager.processes[x]['script']}"
            )
            
            if selected_process:
                try:
                    logs = manager.get_logs(selected_process, max_lines=100)
                    
                    if logs:
                        log_container = st.container()
                        with log_container:
                            for log in reversed(logs):  # Mostrar logs mais recentes primeiro
                                timestamp = datetime.fromisoformat(log['timestamp']).strftime("%H:%M:%S")
                                st.text(f"[{timestamp}] {log['message']}")
                    else:
                        st.info("Nenhum log disponível para este processo.")
                except Exception as e:
                    st.error(f"Erro ao carregar logs: {e}")
        except Exception as e:
            st.error(f"Erro ao listar processos: {e}")
    
    # Auto-refresh
    if st.button("🔄 Atualizar"):
        st.rerun()
    
    # Auto-refresh automático a cada 5 segundos
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()