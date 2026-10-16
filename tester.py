import time
import numpy as np
import matplotlib.pyplot as plt
from simulated_annealing import parse_input_file, SimulatedAnnealing


def run_tests(
    file_path: str,
    schedule1: int = 2,
    schedule2: int = 8,
    T0: float = 100.0,
    TN: float = 0.0001,
    flip_probability: float = 0.01,
    eval_max: int = 200000,
    num_runs: int = 10
):

    # 1. Leitura da instância de entrada
    num_vars, clauses = parse_input_file(file_path)
    total_clauses = len(clauses)

    # Definindo as 4 configurações de teste
    schedules = [schedule1, schedule2]
    samax_values = [1, 100]

    configurations = []
    for sched in schedules:
        for samax in samax_values:
            configurations.append({
                'label': f'Schedule {sched} (SAmax={samax})',
                'schedule': sched,
                'SAmax': samax
            })

    results = {}

    print("=" * 70)
    print(f" INICIANDO EXPERIMENTOS SA 3-SAT: {file_path}")
    print("=" * 70)
    print(f"Variáveis: {num_vars} | Cláusulas: {total_clauses}")
    print(f"Parâmetros: T0={T0}, TN={TN}, FlipProb={flip_probability}, EvalMax={eval_max}, Execuções por Config={num_runs}\n")

    # 2. Execução das simulações
    for config in configurations:
        label = config['label']
        sched = config['schedule']
        samax = config['SAmax']

        print(f"Executando {label} ({num_runs}x)...")

        config_results = {
            'best_values': [],
            'best_solutions': [],
            'histories': [],
            'histories_best': [],
            'times': []
        }

        for run in range(num_runs):
            start_time = time.perf_counter()

            sa = SimulatedAnnealing(
                num_vars=num_vars,
                clauses=clauses,
                SAmax=samax,
                initial_temperature_T0=T0,
                final_temperature_TN=TN,
                eval_max=eval_max,
                flip_probability=flip_probability
            )

            best_sol, best_val, history, history_best = sa.solve(sched)
            elapsed = time.perf_counter() - start_time

            config_results['best_values'].append(best_val)
            config_results['best_solutions'].append(best_sol)
            config_results['histories'].append(history)
            config_results['histories_best'].append(history_best)
            config_results['times'].append(elapsed)

        results[label] = config_results

    # 3. Cálculo da Média e Desvio-Padrão
    print("\n" + "=" * 70)
    print(" RESULTADOS ESTATÍSTICOS (Cláusulas Não Satisfeitas - Minimização)")
    print("=" * 70)
    print(f"{'Configuração':<28} | {'Média':<8} | {'Desvio Padrão':<12} | {'Melhor':<8} | {'Pior':<8}")
    print("-" * 70)

    boxplot_data = []
    labels = []

    for label, res in results.items():
        vals = res['best_values']
        mean_val = np.mean(vals)
        std_val = np.std(vals)
        best_val = min(vals)
        worst_val = max(vals)

        print(f"{label:<28} | {mean_val:<8.2f} | {std_val:<12.2f} | {best_val:<8} | {worst_val:<8}")

        boxplot_data.append(vals)
        labels.append(label)

    print("=" * 70)

    # 4. Geração dos Gráficos de Convergência (1 gráfico para cada configuração)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (label, res) in enumerate(results.items()):
        # Seleciona a execução mediana para ilustrar a convergência
        best_vals = res['best_values']
        rep_idx = int(np.argsort(best_vals)[len(best_vals) // 2])

        rep_history = res['histories'][rep_idx]
        rep_history_best = res['histories_best'][rep_idx]

        # Razão de cláusulas não satisfeitas
        ratio = [v / total_clauses for v in rep_history]
        ratio_best = [v / total_clauses for v in rep_history_best]
        iterations = range(len(rep_history))

        ax = axes[idx]
        ax.plot(iterations, ratio, label='FO Atual', color='blue')
        ax.plot(iterations, ratio_best, label='Melhor FO', color='tab:red', linewidth=1.5)
        ax.set_title(f'Convergência - {label}')
        ax.set_xlabel('Avaliações de FO')
        ax.set_ylabel('Cláusulas Falsas / Total')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

    plt.tight_layout()
    plt.show()

    # 5. Geração do Box-plot comparativo
    plt.figure(figsize=(10, 6))
    plt.boxplot(boxplot_data, labels=labels, showmeans=True)
    plt.title('Comparação do Desempenho das Configurações (10 Execuções)')
    plt.ylabel('Número de Cláusulas Não Satisfeitas')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()

    return results