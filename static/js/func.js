function makeRequest(url, method, data={}, callback) {
  let requestOptions = {
    method: method,
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
  };

  if (method === 'GET') {
    const params = new URLSearchParams(data);
    url += '?' + params;
  } else {
    requestOptions.body = JSON.stringify(data);
  }

  fetch(url, requestOptions)
    .then(response => response.json())
//    .then(response => response.text())
    .then(result => callback(result))
    .catch(error => console.error(error));
}


async function send(data){
    if (data.headers == undefined) {
        headers = { "Accept": "application/json", "Content-Type": "application/json" };
    } else {
        headers = data.headers;
    }

    const response = await fetch(data.url, {
            method: data.method,
            headers: headers,
            body: JSON.stringify(data.body)
        });
        if (response.ok) {
            const data = await response.json();
            data.success(data);
        }
        else
            console.log(response);
}

const login = async (username, password) => {
  const response = await fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return true;
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
};