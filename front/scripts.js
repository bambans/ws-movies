// Atualizar scripts.js para suportar novos endpoints
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

const addNewUserForm = document.getElementById("add-user-form");
if (addNewUserForm) {
  addNewUserForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("user-name").value;
    const email = document.getElementById("user-email").value;
    const number = document.getElementById("user-number").value;
    try {
      const result = await fetchData("/register", {
        name,
        email,
        number,
      });
      document.getElementById("add-user-result").innerText = JSON.stringify(
        result,
        null,
        2,
      );
    } catch (error) {
      document.getElementById("add-user-result").innerText =
        "Error adding user.";
    }
  });
}

// Adicionar evento para cadastrar avaliações
const ratingForm = document.getElementById("rating-form");
if (ratingForm) {
  ratingForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const user = document.getElementById("rating-user").value;
    const movie = document.getElementById("rating-movie").value;
    const rating = document.getElementById("rating-value").value;
    try {
      const result = await fetchData("/add_rating", {
        user,
        movie,
        rating,
      });
      document.getElementById("rating-result").innerText = JSON.stringify(
        result,
        null,
        2,
      );
    } catch (error) {
      document.getElementById("rating-result").innerText =
        "Error submitting rating.";
    }
  });
}

// Adicionar evento para cadastrar preferências
const preferenceForm = document.getElementById("preference-form");
if (preferenceForm) {
  preferenceForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const user = document.getElementById("preference-user").value;
    const preference = document.getElementById("preference-value").value;
    try {
      const result = await fetchData("/add_preference", {
        user,
        preference,
      });
      document.getElementById("preference-result").innerText = JSON.stringify(
        result,
        null,
        2,
      );
    } catch (error) {
      document.getElementById("preference-result").innerText =
        "Error submitting preference.";
    }
  });
}

// Adicionar eventos para listar filmes e preferências
const listMoviesForm = document.getElementById("list-movies-form");
if (listMoviesForm) {
  listMoviesForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const result = await fetchData("/movie");
      document.getElementById("list-movies-result").innerText = JSON.stringify(
        result,
        null,
        2,
      );
    } catch (error) {
      document.getElementById("list-movies-result").innerText =
        "Error fetching movies.";
    }
  });
}

// const listPreferencesForm = document.getElementById("list-preferences-form");
// if (listPreferencesForm) {
//   listPreferencesForm.addEventListener("submit", async (event) => {
//     event.preventDefault();
//     const name = document.getElementById("list-preferences-user").value;
//     try {
//       const result = await fetchData("/user/preferences", { name });
//       document.getElementById("list-preferences-result").innerText =
//         // JSON.stringify(result, null, 1);
//         result;
//     } catch (error) {
//       console.log(error);
//       document.getElementById("list-preferences-result").innerText =
//         "Error fetching preferences.";
//     }
//   });
// }

const listPreferencesForm = document.getElementById("list-preferences-form");
if (listPreferencesForm) {
  listPreferencesForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("list-preferences-user").value;

    try {
      const result = await fetchData("/user/preferences", { name });
      document.getElementById("list-preferences-result").innerText =
        JSON.stringify(result, null, 2); // Pretty-print the JSON
    } catch (error) {
      console.error("Error fetching preferences:", error);
      document.getElementById("list-preferences-result").innerText =
        "Error fetching preferences. Please try again later.";
    }
  });
}
