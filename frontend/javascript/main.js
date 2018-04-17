import '../styles/main.scss'

import 'whatwg-fetch'
import L from 'leaflet'

window.loadMap = function (options) {
  var mapEl = document.querySelector('.food-map')
  var map = L.map(mapEl, {
    center: [options.latitude || 52.518611, options.longitude || 13.408333],
    zoom: 12,
    scrollWheelZoom: false
  })
  var tileUrl = '//cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'

  var defaultTileLayer = new L.TileLayer(tileUrl, {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
  })
  map.attributionControl.setPrefix('')
  map.addLayer(defaultTileLayer)

  var mapButton = document.getElementById('food-map-button')
  mapButton.addEventListener('click', (e) => {
    search()
  })
  search()

  function search () {
    let latlng = map.getCenter()
    let bounds = map.getBounds()
    let radius = Math.min(
      map.distance(
        bounds.getNorthEast(),
        bounds.getNorthWest()
      ),
      map.distance(
        bounds.getNorthEast(),
        bounds.getSouthEast()
      )
    )
    window.fetch(`/api/v1/venue/?lat=${latlng.lat}&lng=${latlng.lng}&radius=${radius}&categories=bar`)
      .then((response) => {
        return response.json()
      }).then((data) => {
        data.forEach((r) => {
          var marker = L.marker([r.lat, r.lng]).addTo(map)
          marker.bindPopup(`
            <h3>${r.name}</h3>
            <a class="btn btn-primary" href="./anfragen/?ident=${encodeURIComponent(r.ident)}">Anfragen</a>
          `)
        })
      })
  }
}
