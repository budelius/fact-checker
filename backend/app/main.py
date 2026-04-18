from fastapi import FastAPI


app = FastAPI(title="Fact Checker API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fact-checker-backend"}


@app.get("/contracts")
def contracts() -> dict[str, str]:
    return {
        "identity": "uuid",
        "metadata_store": "mongodb",
        "vector_store": "qdrant",
        "vault": "markdown",
    }
