export async function getDiagnosis(symptom) {
    const response = await fetch("http://localhost:8000/diagnose/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ symptom }),
    });
    const data = await response.json();
    return data;
  }
  