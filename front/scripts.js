const baseUrl = "http://localhost:5000";

async function fetchData(endpoint, data = null) {
  const response = await fetch(`${baseUrl}${endpoint}`, {
    method: data ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    body: data ? JSON.stringify(data) : null,
  });
  return response.json();
}

document
  .getElementById("query-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = document.getElementById("query").value;
    try {
      const result = await fetchData("/query", { query });
      document.getElementById("query-result").innerText = JSON.stringify(
        result,
        null,
        2,
      );
    } catch (error) {
      document.getElementById("query-result").innerText =
        "Error fetching data.";
    }
  });

document
  .getElementById("movie-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = document.getElementById("movie-title").value;
    try {
      const result = await fetchData(
        `/movie?title=${encodeURIComponent(title)}`,
      );
      document.getElementById("movie-result").innerText = JSON.stringify(
        result,
        null,
        2,
      );
    } catch (error) {
      document.getElementById("movie-result").innerText =
        "Error fetching data.";
    }
  });
