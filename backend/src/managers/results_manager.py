import pandas as pd
import os

class ResultsManager:
    def __init__(self,
                initial_balance: float,
                broker_fee: float,
                setup_name: str,
                symbol: str,
                timeframe: str,
                start_time: str,
                end_time: str,
                leverage: float = 1.0,
            ) -> None:
        self.results = {}
        self.broker_fee = broker_fee
        self.leverage = leverage
        self.setup_name = setup_name
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_time = start_time
        self.end_time = end_time
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.max_balance = initial_balance
        self.min_balance_since_max = initial_balance
        self.max_drawdown = 0.0

    def initialize_month(self, year: int, month: int) -> None:
        if year not in self.results:
            self.results[year] = {}
        if month not in self.results[year]:
            self.results[year][month] = {
                'open_trades': 0,
                'profitable_trades': 0, #successful trades
                'total_percentage_profit': 0.0, #lucro
                'unprofitable_trades': 0, #failed trades
                'total_percentage_loss': 0.0, #perda percentual total
                'initial_balance': self.current_balance,
                'final_balance': self.current_balance,
                'max_drawdown': self.max_drawdown
            }

    def update_on_trade_open(self, year: int, month: int) -> None:
        self.initialize_month(year, month)
        self.results[year][month]['open_trades'] += 1

        if self.broker_fee > 0:
            self.current_balance -= self.current_balance * ((self.broker_fee * self.leverage) / 100)
            self.results[year][month]['final_balance'] = self.current_balance

    def update_on_gain(self, year: int, month: int, profit_percentage: float) -> None:
        self.initialize_month(year, month)
        self.results[year][month]['profitable_trades'] += 1
        
        position_value = self.current_balance * self.leverage
        gross_profit = position_value * (profit_percentage / 100)
        final_position_value = position_value + gross_profit
        exit_fee = final_position_value * (self.broker_fee / 100)
        net_profit = gross_profit - exit_fee
        self.current_balance += net_profit
        real_percentage_gain = (net_profit / self.current_balance) * 100
        self.results[year][month]['total_percentage_profit'] += real_percentage_gain
        self.results[year][month]['final_balance'] = self.current_balance

        if self.current_balance > self.max_balance:
            self.max_balance = self.current_balance
            self.min_balance_since_max = self.current_balance

    def update_on_loss(self, year: int, month: int, loss_percentage: float) -> None:
        self.initialize_month(year, month)
        self.results[year][month]['unprofitable_trades'] += 1

        position_value = self.current_balance * self.leverage
        gross_loss = position_value * (loss_percentage / 100)
        final_position_value = position_value - gross_loss
        exit_fee = final_position_value * (self.broker_fee / 100)
        returned_to_balance = final_position_value - exit_fee
        net_loss = self.current_balance - returned_to_balance
        self.current_balance -= net_loss
        real_percentage_loss = (net_loss / self.current_balance) * 100
        self.results[year][month]['total_percentage_loss'] += real_percentage_loss
        self.results[year][month]['final_balance'] = self.current_balance

        if self.current_balance < self.min_balance_since_max:
            self.min_balance_since_max = self.current_balance

        drawdown = ((self.max_balance - self.min_balance_since_max) / self.max_balance) * 100
        self.results[year][month]['max_drawdown'] = max(self.max_drawdown, drawdown)

        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

    def get_results(self) -> None:
        print("Resultados por ano e mês:")
        for year in self.results:
            print(f"Ano: {year}")
            print(f"  Operações realizadas: {sum(self.results[year][month]['open_trades'] for month in self.results[year])}")

            try:
                print(f"  Taxa de acerto: {sum(
                        self.results[year][month]['profitable_trades'] for month in self.results[year]
                    ) / sum(
                        self.results[year][month]['open_trades'] for month in self.results[year]
                    ) * 100:.2f}%")
            except ZeroDivisionError:
                print("  Taxa de acerto: 0")

            print(f"  Trades de sucesso: {sum(self.results[year][month]['profitable_trades'] for month in self.results[year])}")

            try:
                avg_profit_per_year_trade = (
                    sum(self.results[year][month]['total_percentage_profit'] for month in self.results[year])
                    / sum(self.results[year][month]['profitable_trades'] for month in self.results[year])
                )
                print(f"  Ganho médio por trade: {avg_profit_per_year_trade:.2f}%")
            except ZeroDivisionError:
                print("  Ganho médio por trade: 0")
            
            print(f"  Trades em prejuízo: {sum(self.results[year][month]['unprofitable_trades'] for month in self.results[year])}")
            
            try:
                avg_loss_per_trade = (
                    sum(self.results[year][month]['total_percentage_loss'] for month in self.results[year])
                    / sum(self.results[year][month]['unprofitable_trades'] for month in self.results[year])
                )
                print(f"  Perda média por trade: {avg_loss_per_trade:.2f}%")
            except ZeroDivisionError:
                print("  Perda média por trade: 0")

            print(f"  Drawdown máximo do ano: {max(self.results[year][month]['max_drawdown'] for month in self.results[year]):.2f}%")

            initial_balance = self.results[year][list(self.results[year].keys())[0]]['initial_balance']
            final_balance = self.results[year][list(self.results[year].keys())[-1]]['final_balance']
            print(f"  Resultado final: {(final_balance / initial_balance - 1) * 100:.2f}%")

            print(f"  Saldo inicial: {initial_balance:.2f}")
            print(f"  Saldo final: {final_balance:.2f}")
            print("Detalhes mensais:")
            for month in self.results[year]:
                print(f"  Mês: {month}")
                print(f"    Operações realizadas: {self.results[year][month]['open_trades']}")
                month_total_trades = self.results[year][month]['open_trades']
                month_success_trades = self.results[year][month]['profitable_trades']

                try:
                    month_success_rate = (month_success_trades / month_total_trades) * 100
                    print(f"    Taxa de acerto: {month_success_rate:.2f}%")
                except ZeroDivisionError:
                    print("    Taxa de acerto: 0")  

                print(f"    Trades de sucesso: {self.results[year][month]['profitable_trades']}")

                try:
                    avg_profit_per_month_trade = (
                        self.results[year][month]['total_percentage_profit'] / self.results[year][month]['profitable_trades']
                    )
                    print(f"    Ganho médio por trade: {avg_profit_per_month_trade:.2f}%")
                except ZeroDivisionError:
                    print("    Ganho médio por trade: 0")
                
                print(f"    Trades em prejuízo: {self.results[year][month]['unprofitable_trades']}")

                try:
                    avg_loss_per_month_trade = (
                        self.results[year][month]['total_percentage_loss'] / self.results[year][month]['unprofitable_trades']
                    )
                    print(f"    Perda média por trade: {avg_loss_per_month_trade:.2f}%")
                except ZeroDivisionError:
                    print("    Perda média por trade: 0")

                print(f"    Drawdown máximo: {self.results[year][month]['max_drawdown']:.2f}%")
                month_initial_balance = self.results[year][month]['initial_balance']
                month_final_balance = self.results[year][month]['final_balance']
                print(f"    Resultado final: {(month_final_balance / month_initial_balance - 1) * 100:.2f}%")
                print(f"    Saldo inicial: {self.results[year][month]['initial_balance']:.2f}")
                print(f"    Saldo final: {self.results[year][month]['final_balance']:.2f}")
                print("-------------------")
        print("Resumo geral:")
        total_trades = sum(
            self.results[year][month]['open_trades'] for year in self.results for month in self.results[year]
        )
        print(f"Operações realizadas: {total_trades}")

        total_successful_trades = sum(
            self.results[year][month]['profitable_trades'] for year in self.results for month in self.results[year]
        )

        try:
            success_rate = (total_successful_trades / total_trades) * 100
            print(f"Taxa de acerto: {success_rate:.2f}%")
        except ZeroDivisionError:
            print("Taxa de acerto: 0")

        print(f"Trades de sucesso: {total_successful_trades}")

        try:
            avg_profit_per_trade = (
                sum(
                    self.results[year][month]['total_percentage_profit'] for year in self.results for month in self.results[year]
                ) / total_successful_trades
            )
            print(f"Ganho médio por trade: {avg_profit_per_trade:.2f}%")
        except ZeroDivisionError:
            print("Ganho médio por trade: 0")

        total_failed_trades = sum(
            self.results[year][month]['unprofitable_trades'] for year in self.results for month in self.results[year]
        )
        print(f"Trades em prejuízo: {total_failed_trades}")

        try:
            avg_loss_per_trade = (
                sum(
                    self.results[year][month]['total_percentage_loss'] for year in self.results for month in self.results[year]
                ) / total_failed_trades
            )
            print(f"Perda média por trade: {avg_loss_per_trade:.2f}%")
        except ZeroDivisionError:
            print("Perda média por trade: 0")
            
        print(f"Drawdown máximo: {self.max_drawdown:.2f}%")

        print(f"Resultado final: {(self.current_balance / self.initial_balance - 1) * 100:.2f}%")

        print(f"Saldo inicial: {self.initial_balance:.2f}")
        print(f"Saldo final: {self.current_balance:.2f}")
        print(f'Cripto: {self.symbol}')
        print(f'Tempo gráfico: {self.timeframe}')
        print(f"Alavancagem: {self.leverage}")
        print(f"Período: {self.start_time} - {self.end_time}")
        print(f"Setup: {self.setup_name}")

    def summarize_results(self) -> None:
        print("Resumo por ano e geral:")
        for year in self.results:
            initial_balance = self.results[year][list(self.results[year].keys())[0]]['initial_balance']
            final_balance = self.results[year][list(self.results[year].keys())[-1]]['final_balance']
            total_trades = sum(self.results[year][month]['open_trades'] for month in self.results[year])
            successful_trades = sum(self.results[year][month]['profitable_trades'] for month in self.results[year])

            print(f"Ano: {year}")
            print(f"  Operações realizadas: {total_trades}")
            print(f"  Trades de sucesso: {successful_trades}")
            try:
                success_rate = (successful_trades / total_trades) * 100
                print(f"  Taxa de acerto: {success_rate:.2f}%")
            except ZeroDivisionError:
                print("  Taxa de acerto: 0")
            print(f"  Drawdown máximo do ano: {max(self.results[year][month]['max_drawdown'] for month in self.results[year]):.2f}%")
            print(f"  Resultado final do ano: {(final_balance / initial_balance - 1) * 100:.2f}%")
            print(f"  Saldo inicial: {initial_balance:.2f}")
            print(f"  Saldo final: {final_balance:.2f}")
            print("-------------------")

        print("Resumo geral:")
        print(f"Saldo inicial: {self.initial_balance:.2f}")
        print(f"Saldo final: {self.current_balance:.2f}")
        print(f"Resultado final: {(self.current_balance / self.initial_balance - 1) * 100:.2f}%")
        print(f"Drawdown máximo geral: {self.max_drawdown:.2f}%")
        print(f"Setup: {self.setup_name}")

    def save_summarized_results_to_xlsx(self, filename: str = 'data/results/procedural/results.xlsx') -> None:
        total_trades = sum(self.results[year][month]['open_trades'] for year in self.results for month in self.results[year])
        total_successful_trades = sum(
            self.results[year][month]['profitable_trades'] for year in self.results for month in self.results[year]
        )

        try:
            success_rate = (total_successful_trades / total_trades) * 100
        except ZeroDivisionError:
            success_rate = 0

        try:
            avg_profit_per_trade = (
                sum(
                    self.results[year][month]['total_percentage_profit'] for year in self.results for month in self.results[year]
                ) / total_successful_trades
            )
        except ZeroDivisionError:
            avg_profit_per_trade = 0

        total_failed_trades = sum(
            self.results[year][month]['unprofitable_trades'] for year in self.results for month in self.results[year]
        )
        
        try:
            avg_loss_per_trade = (
                sum(
                    self.results[year][month]['total_percentage_loss'] for year in self.results for month in self.results[year]
                ) / total_failed_trades
            )
        except ZeroDivisionError:
            avg_loss_per_trade = 0
        final_result = (self.current_balance / self.initial_balance - 1) * 100

        data = {
            'Moeda': [self.symbol],
            'Tempo Gráfico': [self.timeframe],
            'Alavancagem': [self.leverage],
            'Início': [self.start_time],
            'Fim': [self.end_time],
            'Setup': [self.setup_name],
            'Trades': [total_trades],
            'Taxa de acerto': [f'{success_rate:.2f}%'],
            'Trades c/ lucro': [total_successful_trades],
            'Ganho médio': [f'{avg_profit_per_trade:.2f}%'],
            'Trades c/ perda': [total_failed_trades],
            'Perda média': [f'{avg_loss_per_trade:.2f}%'],
            'Drawdown máximo': [f'{self.max_drawdown:.2f}%'],
            'Resultado': [f'{final_result:.2f}%'],
            'Saldo inicial': [self.initial_balance],
            'Saldo final': [f'{self.current_balance:.2f}'],
        }

        df = pd.DataFrame(data)

        if os.path.exists(filename):
            with pd.ExcelWriter(filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                existing_df = pd.read_excel(filename, sheet_name='Resultados')
                startrow = len(existing_df) + 1

                df.to_excel(writer, sheet_name='Resultados', index=False, header=False, startrow=startrow)
        else:
            os.makedirs("data/results/procedural", exist_ok=True)
            df.to_excel(filename, sheet_name='Resultados', index=False)

        print (f"Resultados salvos em {filename}")