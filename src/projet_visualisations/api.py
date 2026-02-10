from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
from .llm import VizOrchestrator

app = FastAPI(title="Dauphine Viz AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = VizOrchestrator()


def clean_generated_code(raw_code: str) -> str:
    clean_c = raw_code.replace("```python", "").replace("```", "").strip()
    lines = clean_c.split("\n")
    safe_lines = []
    for line in lines:
        if any(bad in line for bad in ["pd.read_csv", "import pandas", "pd.DataFrame", "fig.show()"]):
            continue
        safe_lines.append(line)
    return '\n'.join(safe_lines)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), query: str = Form(...)):
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        return {"error": f"Unable to read CSV: {e}"}

    props = orchestrator.get_propositions(df.head(5).to_string(), query)
    if not props:
        return {"error": "No proposals generated"}

    results = []

    for p in props:
        desc = f"{p.get('titre','')}: {p.get('justification','')}"
        raw_code = orchestrator.generate_code(desc, df.columns.tolist(), len(df))
        clean_code = clean_generated_code(raw_code)

        try:
            import plotly.express as px
            ldict = {'df': df, 'px': px}
            exec(clean_code, globals(), ldict)
            if 'fig' in ldict:
                fig = ldict['fig']
                # fig.to_json() returns a JSON string; convert to object
                fig_json = json.loads(fig.to_json())
            else:
                fig_json = None
        except Exception as e:
            fig_json = None

        results.append({
            "titre": p.get('titre'),
            "justification": p.get('justification'),
            "insights": p.get('insights', {}),
            "fig": fig_json,
            "code": clean_code,
        })

    return {"results": results}
