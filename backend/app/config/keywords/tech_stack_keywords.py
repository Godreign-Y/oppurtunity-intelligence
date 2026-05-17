"""
app/config/keywords/tech_stack_keywords.py

Technology detection keyword list used by career, blog, and hiring pipelines.

Used by:
- app/utils/normalization.py (detect_technologies_from_text)
- app/services/hiring/processor.py (extract_tech_stack)

To add a new technology: append its lowercase name to TECH_STACK_KEYWORDS.
"""

# Comprehensive list of technology names for keyword detection in job descriptions,
# blog posts, and hiring signals. All entries must be lowercase.
TECH_STACK_KEYWORDS: list[str] = [
    # Container & Orchestration
    "kubernetes", "k8s", "docker", "helm", "rancher", "openshift",
    "argocd", "flux", "istio", "envoy", "linkerd",

    # CI/CD & DevOps
    "terraform", "ansible", "puppet", "chef", "github actions", "gitlab ci",
    "jenkins", "circleci", "buildkite", "drone", "spinnaker", "tekton",
    "packer", "vault",

    # Cloud Providers
    "aws", "gcp", "azure", "cloudflare", "digitalocean", "linode",

    # Observability & Monitoring
    "grafana", "prometheus", "datadog", "newrelic", "dynatrace",
    "opentelemetry", "jaeger", "zipkin", "splunk", "elastic", "kibana",

    # Messaging & Streaming
    "kafka", "rabbitmq", "nats", "pulsar", "sqs", "eventbridge",

    # Databases
    "postgresql", "mysql", "mongodb", "redis", "cassandra", "dynamodb",
    "elasticsearch", "opensearch", "clickhouse", "cockroachdb", "tidb",

    # Data Platform
    "airflow", "spark", "flink", "dbt", "snowflake", "bigquery",
    "redshift", "databricks", "delta lake", "iceberg", "nifi",

    # AI / ML
    "pytorch", "tensorflow", "jax", "triton", "vllm", "onnx",
    "hugging face", "langchain", "llamaindex", "openai", "anthropic",
    "ray", "kubeflow", "mlflow", "bentoml", "seldon",

    # Backend Frameworks
    "fastapi", "django", "flask", "rails", "express", "nestjs",
    "spring boot", "quarkus", "grpc", "graphql",

    # Frontend
    "react", "next.js", "vue", "angular", "svelte", "typescript",

    # Languages
    "python", "java", "go", "rust", "scala", "elixir", "kotlin",
    "c++", "ruby", "nodejs",

    # Infra-as-Code & Config
    "pulumi", "crossplane", "cdk", "cloudformation",

    # Security
    "vault", "keycloak", "okta", "auth0", "zero trust", "soc2",
]
