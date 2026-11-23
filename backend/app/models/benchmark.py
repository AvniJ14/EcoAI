
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship

from app.database.database import Base


# ==================================================
# TABLE 1: BENCHMARK RUNS
# ==================================================

class BenchmarkRun(Base):

    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)

    dataset_id = Column(String(100))
    dataset_name = Column(String(150), nullable=False)

    task_type = Column(String(30), default="classification")

    total_models = Column(Integer, default=0)

    experiment_runs = Column(Integer, default=5)

    inference_repeats = Column(Integer, default=100)

    status = Column(String(30), default="Completed")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    model_results = relationship(
        "ModelResult",
        back_populates="benchmark",
        cascade="all, delete-orphan"
    )


# ==================================================
# TABLE 2: MODEL RESULTS
# ==================================================

class ModelResult(Base):

    __tablename__ = "model_results"

    id = Column(Integer, primary_key=True, index=True)

    benchmark_id = Column(
        Integer,
        ForeignKey("benchmark_runs.id"),
        nullable=False
    )

    model_id = Column(String(100))
    model_name = Column(String(150), nullable=False)

    task_type = Column(String(30), default="classification")

    # Classification metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)

    accuracy_std = Column(Float)
    precision_std = Column(Float)
    recall_std = Column(Float)
    f1_score_std = Column(Float)

    # Regression metrics
    mae = Column(Float)
    mse = Column(Float)
    rmse = Column(Float)
    r2_score = Column(Float)

    mae_std = Column(Float)
    mse_std = Column(Float)
    rmse_std = Column(Float)
    r2_score_std = Column(Float)

    # Time metrics
    training_time_seconds = Column(Float)
    training_time_std_seconds = Column(Float)

    inference_time_seconds = Column(Float)
    median_inference_time_seconds = Column(Float)
    inference_time_std_seconds = Column(Float)

    # Resource metrics
    cpu_usage_percent = Column(Float)
    memory_before_mb = Column(Float)
    memory_after_mb = Column(Float)
    memory_change_mb = Column(Float)

    # Energy metrics
    training_energy_kwh = Column(Float)
    inference_energy_kwh = Column(Float)
    energy_consumed_kwh = Column(Float)
    energy_std_kwh = Column(Float)

    # Carbon metrics
    training_carbon_kg = Column(Float)
    inference_carbon_kg = Column(Float)
    carbon_emissions_kg = Column(Float)

    # EcoScore
    accuracy_percentage = Column(Float)
    r2_percentage = Column(Float)
    quality_score = Column(Float)
    energy_efficiency_score = Column(Float)
    eco_score = Column(Float)

    eligible = Column(Boolean, default=False)

    rank = Column(Integer)

    recommendation_status = Column(String(50))

    eligibility_reason = Column(Text)

    benchmark = relationship(
        "BenchmarkRun",
        back_populates="model_results"
    )

    experiment_metrics = relationship(
        "ExperimentMetric",
        back_populates="model_result",
        cascade="all, delete-orphan"
    )


# ==================================================
# TABLE 3: INDIVIDUAL EXPERIMENT METRICS
# ==================================================

class ExperimentMetric(Base):

    __tablename__ = "experiment_metrics"

    id = Column(Integer, primary_key=True, index=True)

    model_result_id = Column(
        Integer,
        ForeignKey("model_results.id"),
        nullable=False
    )

    run_number = Column(Integer, nullable=False)

    # Classification metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)

    # Regression metrics
    mae = Column(Float)
    mse = Column(Float)
    rmse = Column(Float)
    r2_score = Column(Float)

    # Time metrics
    training_time_seconds = Column(Float)
    inference_time_seconds = Column(Float)
    total_inference_time_seconds = Column(Float)

    # Resource metrics
    cpu_usage_percent = Column(Float)
    memory_before_mb = Column(Float)
    memory_after_mb = Column(Float)
    memory_change_mb = Column(Float)

    # Energy metrics
    training_energy_kwh = Column(Float)
    inference_energy_kwh = Column(Float)
    total_energy_kwh = Column(Float)

    # Carbon metrics
    training_carbon_kg = Column(Float)
    inference_carbon_kg = Column(Float)
    total_carbon_kg = Column(Float)

    model_result = relationship(
        "ModelResult",
        back_populates="experiment_metrics"
    )
