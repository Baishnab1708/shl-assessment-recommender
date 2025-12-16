async function getRecommendations() {
  const query = document.getElementById("query").value.trim();
  const topK = document.getElementById("topK").value;
  const resultsDiv = document.getElementById("results");

  resultsDiv.innerHTML = "";

  if (!query) {
    alert("Please enter a query");
    return;
  }

  resultsDiv.innerHTML = "<p>Loading recommendations...</p>";

  try {
    const response = await fetch("http://localhost:8000/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: query,
        top_k: Number(topK)
      })
    });

    if (!response.ok) {
      throw new Error("API Error");
    }

    const data = await response.json();
    renderResults(data.recommended_assessments);
  } catch (err) {
    resultsDiv.innerHTML = "<p style='color:red'>Failed to fetch recommendations</p>";
  }
}

function renderResults(items) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";

  if (!items || items.length === 0) {
    resultsDiv.innerHTML = "<p>No recommendations found.</p>";
    return;
  }

  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "result-card";

    card.innerHTML = `
      <h3>${item.name}</h3>
      <div class="meta">${item.test_type} • ${item.duration}</div>
      <p>${item.description}</p>
      <div class="meta">
        Remote: ${item.remote_support} |
        Adaptive: ${item.adaptive_support}
      </div>
      <a href="${item.url}" target="_blank">View Assessment →</a>
    `;

    resultsDiv.appendChild(card);
  });
}
