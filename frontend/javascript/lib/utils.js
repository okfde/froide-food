function renderDate (date) {
  let d = (new Date(date))
  return `${d.getDate()}.${d.getMonth()}.${d.getFullYear()}`
}

function getPlaceStatus (place) {
  if (place.requests.length === 0) {
    return 'normal'
  }
  if (place.last_status === 'resolved') {
    if (place.last_resolution === 'successful' ||
        place.last_resolution === 'partially_successful') {
      return 'success'
    } else if (place.last_resolution === 'refused') {
      return 'failure'
    } else {
      return 'complete'
    }
  } else if (place.last_status === 'awaiting_response' ||
             place.last_status === 'awaiting_user_confirmation') {
    return 'pending'
  }
  return 'normal'
}

const PINS = {}

function getPinURL (color) {
  if (PINS[color] === undefined) {
    let svg = `<?xml version="1.0" encoding="UTF-8"?><svg viewBox="0 0 8.9999998 11.800001" xml:space="preserve" xmlns="http://www.w3.org/2000/svg"> <defs><filter id="a" x="-.10828" y="-.086222" width="1.2166" height="1.1724" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="0.388"/></filter></defs> <path d="m4.5 0.90339c1.1 0 2.2 0.5 3 1.3 0.8 0.9 1.3 1.9 1.3 3.1s-0.5 2.5-1.3 3.3l-3 3.1-3-3.1c-0.8-0.8-1.3-2-1.3-3.3 0-1.2 0.4-2.2 1.3-3.1 0.8-0.8 1.9-1.3 3-1.3z" fill="#646464" fill-opacity=".39216" filter="url(#a)"/> <path fill="${color}" d="m4.5 0.2c1.1 0 2.2 0.5 3 1.3 0.8 0.9 1.3 1.9 1.3 3.1s-0.5 2.5-1.3 3.3l-3 3.1-3-3.1c-0.8-0.8-1.3-2-1.3-3.3 0-1.2 0.4-2.2 1.3-3.1 0.8-0.8 1.9-1.3 3-1.3z"/> </svg>`
    // return `data:image/svg+xml;utf8,` + svg.replace(/#/g, '%23')
    PINS[color] = window.URL.createObjectURL(new window.Blob([svg], {type: 'image/svg+xml'}))
  }
  return PINS[color]
}

function getPinColor (status, selected) {
  if (selected) {
    switch (status) {
      case 'normal':
        return '#003d7f'
      case 'pending':
        return '#e1a300'
      case 'success':
      case 'complete':
        return '#0a8927'
      case 'failure':
        return '#be1727'
    }
  } else {
    switch (status) {
      case 'normal':
        return '#007bff'
      case 'pending':
        return '#ffc107'
      case 'success':
      case 'complete':
        return '#28a745'
      case 'failure':
        return '#dc3545'
    }
  }
}

function getQueryVariable (variable) {
  var query = window.location.search.substring(1)
  var vars = query.split('&')
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split('=')
    if (decodeURIComponent(pair[0]) === variable) {
      return decodeURIComponent(pair[1])
    }
  }
}

function canUseLocalStorage (window) {
  try {
    const key = '__canary_key__'
    window.localStorage.setItem(key, key)
    window.localStorage.removeItem(key)
    return true
  } catch (e) {
    return false
  }
}

export {
  getQueryVariable,
  renderDate,
  getPlaceStatus,
  getPinURL,
  getPinColor,
  canUseLocalStorage
}
