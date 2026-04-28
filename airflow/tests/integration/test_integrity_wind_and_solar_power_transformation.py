from airflow.models import DagBag


class TestWindAndSolarPowerTransformationDAG:
    """Test the wind_and_solar_power_transformation DAG."""

    def test_dag_loaded(self, dag_wind_and_solar_power_transformation: DagBag) -> None:
        """Test if the DAG is correctly loaded."""
        assert DagBag().import_errors == {}, "Improper import"
        assert dag_wind_and_solar_power_transformation.id in DagBag().dags, f"DAG '{dag_wind_and_solar_power_transformation.id}' is missing"
        assert dag_wind_and_solar_power_transformation is not None, "DAG object is None"
        assert len(dag_wind_and_solar_power_transformation.tasks) > 0, "No tasks in the DAG"

    def test_dag_has_tags(self, dag_wind_and_solar_power_transformation: DagBag) -> None:
        """Test if the DAG contains the correct tags."""
        assert {"dbt", "half hourly"}.issubset(dag_wind_and_solar_power_transformation.tags), f"Expected tags {'dbt', 'half hourly'}, but got {dag_wind_and_solar_power_transformation.tags}"

    def test_task_count(self, dag_wind_and_solar_power_transformation: DagBag) -> None:
        """Test the number of tasks in the DAG."""
        expected_task_count = 2
        assert len(dag_wind_and_solar_power_transformation.tasks) == expected_task_count, f"Expected 2 tasks, but got {len(dag_wind_and_solar_power_transformation.tasks)}"

    def test_task_dependencies(self, dag_wind_and_solar_power_transformation: DagBag) -> None:
        """Test the dependencies between the tasks."""
        # Define expected upstream and downstream dependencies
        task_deps = {
            "build_dbt_models": ["parameterize"],
        }

        for task_id, upstream_ids in task_deps.items():
            task = dag_wind_and_solar_power_transformation.get_task(task_id)
            assert task is not None, f"Task '{task_id}' is missing in the DAG"
            upstream_tasks = [t.task_id for t in task.upstream_list]
            assert set(upstream_ids) == set(
                upstream_tasks,
            ), f"Task '{task_id}' has incorrect upstream dependencies"
