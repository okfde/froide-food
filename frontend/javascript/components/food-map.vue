<template>
  <div>
    <input type="text" v-model="query"/>
    <button class="btn btn-secondary" @click="search">
      Im aktuellen Bereich suchen
    </button>
    <div class="map-container">
      <l-map ref="map" :zoom="zoomPosition" :center="center">
        <l-tile-layer
          layerType="base" :name="tileProvider.name" :visible="true"
          :url="tileProvider.url" :attribution="tileProvider.attribution"/>

        <l-marker v-for="marker in markers" :lat-lng="marker.position" :title="marker.name" :draggable="false">
          <l-popup>
            <food-popup :data="marker" />
          </l-popup>
        </l-marker>
       </l-map>
     </div>
   </div>
</template>

<script>

import 'whatwg-fetch'

import { LMap, LTileLayer, LControlZoom, LMarker, LPopup } from 'vue2-leaflet'
import FoodPopup from './food-popup'

export default {
  name: 'food-map',
  props: ['config'],
  components: { LMap, LTileLayer, LControlZoom, LMarker, LPopup, FoodPopup
  },
  data () {
    return {
      tileProvider: {
        name: 'Carto',
        url: '//cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      },
      zoomPosition: 12,
      center: [this.config.city.latitude || 52.518611, this.config.city.longitude || 13.408333],
      markers: [],
      query: ''
    }
  },
  mounted () {
    this.map.attributionControl.setPrefix('')
    this.search()
  },
  computed: {
    map () {
      return this.$refs.map.mapObject
    }
  },
  methods: {
    search () {
      let latlng = this.map.getCenter()
      let bounds = this.map.getBounds()
      let radius = Math.min(
        this.map.distance(
          bounds.getNorthEast(),
          bounds.getNorthWest()
        ),
        this.map.distance(
          bounds.getNorthEast(),
          bounds.getSouthEast()
        )
      )
      radius = Math.round(Math.min(radius, 40000))
      let categories = []
      let cats = categories.map((c) => `categories=${encodeURIComponent(c)}`)
      cats = cats.join('&')
      window.fetch(`/api/v1/venue/?lat=${latlng.lat}&lng=${latlng.lng}&radius=${radius}&q=${encodeURIComponent(this.query)}&${cats}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          this.markers = data.map((r) => {
            return {
              position: [r.lat, r.lng],
              ...r
            }
          })
        })
    }
  }
}
</script>

<style lang="scss" scoped>

.map-container {
  width: 100%;
  height: 680px;
}

</style>
