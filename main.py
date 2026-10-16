import sys
import argparse
from tester import run_tests


def main():
    parser = argparse.ArgumentParser(description="Executa os testes do Simulated Annealing para 3-SAT.")
    
    parser.add_argument("file_path", type=str, help="Caminho para o arquivo da instância (.cnf)")
    parser.add_argument("--schedule1", type=int, default=7, help="Número do primeiro esquema de resfriamento (padrão: 1)")
    parser.add_argument("--schedule2", type=int, default=8, help="Número do segundo esquema de resfriamento (padrão: 8)")
    parser.add_argument("--t0", type=float, default=100.0, help="Temperatura inicial T0 (padrão: 100.0)")
    parser.add_argument("--tn", type=float, default=0.0001, help="Temperatura final TN (padrão: 0.0001)")
    parser.add_argument("--flip_prob", type=float, default=0.01, help="Probabilidade de flip de bits (padrão: 0.05)")
    parser.add_argument("--eval_max", type=int, default=2000000, help="Número máximo de avaliações de FO (padrão: 200000)")
    parser.add_argument("--num_runs", type=int, default=10, help="Número de execuções por configuração (padrão: 10)")

    args = parser.parse_args()

    run_tests(
        file_path=args.file_path,
        schedule1=args.schedule1,
        schedule2=args.schedule2,
        T0=args.t0,
        TN=args.tn,
        flip_probability=args.flip_prob,
        eval_max=args.eval_max,
        num_runs=args.num_runs
    )


if __name__ == "__main__":
    main()