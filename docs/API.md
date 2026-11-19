# 📡 Tech Women Data API — Endpoint Reference (`v1.0.0`)

RESTful API built with **FastAPI** and **SQLAlchemy** to serve analytical indicators on female representation in Brazilian Information Technology higher education courses (2009–2024).

- **Base URL (Local):** `http://127.0.0.1:8000`
- **Interactive Docs:** `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **Data Model:** Star Schema (`fact_metrics`, `dim_location`, `dim_program`)
- **Content-Type:** `application/json`
- **Authentication:** None (public read-only API)

---

## 1. Health Check

### `GET /`

Verifies that the FastAPI server is active and accepting HTTP requests without opening a database session.

- **Parameters:** None
- **Success Response (`200 OK`):**
  ```json
  {
    "status": "API ativa e operacional"
  }
  ```
- **Error Codes:** None (does not depend on database connectivity).

---

## 2. Consolidated Global KPIs

### `GET /api/v1/kpis/geral`

Aggregates all records in `fact_metrics` into a single 15-year historical summary (2009–2024), returning absolute totals and female percentages across entrants, active enrolled students, and graduates. Uses `NULLIF(..., 0)` to prevent division-by-zero errors and returns `{}` if the table is empty.

- **Parameters:** None
- **Response Fields (`200 OK`):**

| Field | Type | Description |
| :--- | :--- | :--- |
| `total_ingressantes` | `number` | Cumulative total entrants (2009–2024) |
| `total_ingressantes_mulheres` | `number` | Cumulative female entrants |
| `pct_ingressantes_mulheres` | `float \| null` | Female share among entrants (`%`, rounded to 2 decimal places) |
| `total_matriculados` | `number` | Cumulative total active enrollments |
| `total_matriculados_mulheres` | `number` | Cumulative female active enrollments |
| `pct_matriculados_mulheres` | `float \| null` | Female share among enrolled students (`%`, 2 decimal places) |
| `total_concluintes` | `number` | Cumulative total graduates |
| `total_concluintes_mulheres` | `number` | Cumulative female graduates |
| `pct_concluintes_mulheres` | `float \| null` | Female share among graduates (`%`, 2 decimal places) |

- **Example Request & Response:**
  ```http
  GET /api/v1/kpis/geral HTTP/1.1
  ```
  ```json
  {
    "total_ingressantes": 3379056,
    "total_ingressantes_mulheres": 594235,
    "pct_ingressantes_mulheres": 17.59,
    "total_matriculados": 6297287,
    "total_matriculados_mulheres": 1014784,
    "pct_matriculados_mulheres": 16.11,
    "total_concluintes": 793138,
    "total_concluintes_mulheres": 128182,
    "pct_concluintes_mulheres": 16.16
  }
  ```
- **Error Codes:**
  - `500 Internal Server Error`: Database connection or query execution failure.

---

## 3. Historical Temporal Evolution

### `GET /api/v1/metricas/evolucao-temporal`

Groups `fact_metrics` by `year` in ascending chronological order (`ORDER BY year ASC`), returning annual totals and female representation percentages for time-series visualizations.

- **Parameters:** None
- **Response Fields per Item (`200 OK`):**
  - `year` (`int`): Census reference year (`2009`–`2024`).
  - `total_ingressantes`, `ingressantes_mulheres`, `pct_ingressantes_mulheres`
  - `total_matriculas`, `matriculas_mulheres`, `pct_matriculas_mulheres` *(note: uses `matriculas` rather than `matriculados`)*
  - `total_concluintes`, `concluintes_mulheres`, `pct_concluintes_mulheres`

- **Example Request & Response:**
  ```http
  GET /api/v1/metricas/evolucao-temporal HTTP/1.1
  ```
  ```json
  [
    {
      "year": 2009,
      "total_ingressantes": 82400,
      "ingressantes_mulheres": 14832,
      "pct_ingressantes_mulheres": 18.0,
      "total_matriculas": 245000,
      "matriculas_mulheres": 42875,
      "pct_matriculas_mulheres": 17.5,
      "total_concluintes": 31200,
      "concluintes_mulheres": 5928,
      "pct_concluintes_mulheres": 19.0
    }
  ]
  ```
- **Error Codes:**
  - `500 Internal Server Error`: Database connection or query execution failure.

---

## 4. Geographical Ranking by State (UF)

### `GET /api/v1/metricas/estados`

Joins `fact_metrics` with `dim_location`, filters out missing or undeclared state codes (`state_code IS NOT NULL AND state_code != 'Not reported'`), and orders Brazilian states by total enrollment volume descending (`ORDER BY total_matriculas DESC`).

- **Parameters:** None
- **Response Fields per Item (`200 OK`):**
  - `state_uf` (`str`): Federative Unit abbreviation (e.g., `SP`, `PI`, `AM`).
  - `total_matriculas`, `matriculas_mulheres`, `pct_mulheres_matriculas`
  - `total_concluintes`, `concluintes_mulheres`, `pct_mulheres_concluintes`

- **Example Request & Response:**
  ```http
  GET /api/v1/metricas/estados HTTP/1.1
  ```
  ```json
  [
    {
      "state_uf": "SP",
      "total_matriculas": 2150400,
      "matriculas_mulheres": 374170,
      "pct_mulheres_matriculas": 17.4,
      "total_concluintes": 320908,
      "concluintes_mulheres": 56480,
      "pct_mulheres_concluintes": 17.6
    }
  ]
  ```
- **Error Codes:**
  - `500 Internal Server Error`: Database connection or query execution failure.

---

## 5. Course Ranking by Female Representation

### `GET /api/v1/metricas/cursos`

Joins `fact_metrics` with `dim_program`, applies a post-aggregation volume threshold (`HAVING total_matriculas >= :min_matriculas`) to prevent small-sample distortion, and ranks programs by female enrollment share descending (`ORDER BY pct_mulheres_matriculas DESC`).

- **Query Parameters:**

| Parameter | In | Type | Required | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `min_matriculas` | `query` | `int` | No | `5000` | `>= 0` | Minimum cumulative enrollments required for a course to be ranked |
| `limit` | `query` | `int` | No | `10` | `1` to `500` | Maximum number of courses returned |

- **Response Fields per Item (`200 OK`):**
  - `course_name` (`str`): Standardized uppercase program name from `dim_program`.
  - `total_matriculas`, `matriculas_mulheres`, `pct_mulheres_matriculas`
  - `total_concluintes`, `concluintes_mulheres`, `pct_mulheres_concluintes`

- **Example Request & Response:**
  ```http
  GET /api/v1/metricas/cursos?min_matriculas=10000&limit=2 HTTP/1.1
  ```
  ```json
  [
    {
      "course_name": "GESTAO DA TECNOLOGIA DA INFORMACAO",
      "total_matriculas": 320500,
      "matriculas_mulheres": 67305,
      "pct_mulheres_matriculas": 21.0,
      "total_concluintes": 48900,
      "concluintes_mulheres": 11247,
      "pct_mulheres_concluintes": 23.0
    }
  ]
  ```
- **Error Codes:**
  - `422 Unprocessable Entity`: Invalid parameter type or out-of-range value (`min_matriculas < 0`, `limit < 1`, or `limit > 500`).
  - `500 Internal Server Error`: Database connection or query execution failure.

---

## 6. Dynamic Multi-Dimensional Filter

### `GET /api/v1/metricas/filtrar`

Queries `fact_metrics`, `dim_location`, and `dim_program` using optional cumulative `AND` filters. String inputs (`uf` and `curso`) are automatically normalized to uppercase (`.upper()`), and `curso` performs a substring search (`LIKE CONCAT('%', :curso, '%')`). Results are ordered by `year DESC, total_matriculas DESC`.

> **Note:** Unlike the aggregated endpoints above, this endpoint returns raw absolute counts per `(year, state_uf, course_name)` combination without `pct_*` percentage columns.

- **Query Parameters:**

| Parameter | In | Type | Required | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ano` | `query` | `int` | No | `null` | `2009` to `2024` | Filter by exact reference year |
| `uf` | `query` | `str` | No | `null` | Length `2` | Filter by state abbreviation; case-insensitive (e.g., `pi` → `PI`) |
| `curso` | `query` | `str` | No | `null` | Min length `1` | Partial course name match; case-insensitive (e.g., `ciencia` → `%CIENCIA%`) |
| `limit` | `query` | `int` | No | `50` | `1` to `500` | Maximum number of rows returned |

- **Response Fields per Item (`200 OK`):**
  - `year` (`int`), `state_uf` (`str`), `course_name` (`str`)
  - `total_ingressantes`, `ingressantes_mulheres`
  - `total_matriculas`, `matriculas_mulheres`
  - `total_concluintes`, `concluintes_mulheres`

- **Example Request & Response:**
  ```http
  GET /api/v1/metricas/filtrar?ano=2024&uf=pi&curso=ciencia&limit=10 HTTP/1.1
  ```
  ```json
  [
    {
      "year": 2024,
      "state_uf": "PI",
      "course_name": "CIENCIA DA COMPUTACAO",
      "total_ingressantes": 420,
      "ingressantes_mulheres": 76,
      "total_matriculas": 1680,
      "matriculas_mulheres": 285,
      "total_concluintes": 190,
      "concluintes_mulheres": 38
    }
  ]
  ```
- **Error Codes:**
  - `200 OK` with `[]`: Returned when no records match the provided filters (does not raise `404 Not Found`).
  - `422 Unprocessable Entity`: Invalid parameter type or out-of-range value (`ano` outside `2009–2024`, `uf` length different from `2`, empty `curso`, or `limit` outside `1–500`).
  - `500 Internal Server Error`: Database connection or query execution failure.
