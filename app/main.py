from app.infrastructure.di_container import Container


def main() -> None:
    container = Container()

    # Executed in FK-safe order:
    # contacts -> products -> sale_orders -> sale_order_lines
    use_cases = [
        container.contact_sync_use_case(),
        container.product_sync_use_case(),
        container.sale_order_sync_use_case(),
        container.sale_order_line_sync_use_case(),
    ]

    runs = []
    for use_case in use_cases:
        run = use_case.execute()
        runs.append(run)
        print(
            f"[{run.operation_type}] "
            f"status={run.status.value} "
            f"received={run.records_received} "
            f"saved={run.records_saved} "
            f"updated={run.records_updated} "
            f"failed={run.records_failed}"
        )

    has_errors = any(run.records_failed > 0 for run in runs)
    raise SystemExit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
