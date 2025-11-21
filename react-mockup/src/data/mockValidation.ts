export const mockValidationReport = {
  summary: {
    total_records: 23,
    updated_records: 21,
    failed_records: 2,
    start_time: "2025-11-21 12:35:10",
    end_time: "2025-11-21 12:35:28",
    duration_seconds: 18,
  },
  performance: {
    total_time_seconds: 18.4,
    avg_time_per_record_ms: 800,
    throughput_records_per_second: 1.25,
  },
  errors: {
    count: 2,
    breakdown: [
      {
        error_type: "Foreign key constraint violation",
        count: 1,
        sample_questionids: [156789],
      },
      {
        error_type: "Null constraint violation",
        count: 1,
        sample_questionids: [156790],
      },
    ],
  },
  validation: {
    pre_update_count: 19847,
    post_update_count: 19847,
    data_integrity_check: "passed" as const,
    foreign_key_violations: 0,
    null_constraint_violations: 0,
  },
  rollback_available: true,
  backup_location: "/backups/2025-11-21_123510.sql",
}

