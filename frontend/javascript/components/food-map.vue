<template>
  <div class="container-fluid">
    <div class="searchbar" id="searchbar">
      <div class="input-group">
        <input type="text" v-model="query" class="form-control" placeholder="Restaurant, Döner, etc."  @keydown.enter.prevent="search">
        <div class="input-group-append">
          <button class="btn btn-outline-secondary" type="button" @click="search">
            Suchen
          </button>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-8 order-md-2 map-column">
        <div class="map-container" id="food-map">
          <div v-if="mapMoved" class="redo-search">
            <button class="btn btn-secondary btn-sm" @click="search">
              Im aktuellen Bereich suchen
            </button>
          </div>

          <l-map ref="map" :zoom="zoom" :center="center" :options="mapOptions">
            <l-tile-layer
              layerType="base" :name="tileProvider.name" :visible="true"
              :url="tileProvider.url" :attribution="tileProvider.attribution"/>

            <l-marker v-for="marker in facilities" :key="marker.ident" :lat-lng="marker.position" :title="marker.name" :draggable="false" :icon="marker.icon">
              <l-tooltip :content="marker.name" />
              <l-popup :options="popupOptions">
                <food-popup :data="marker" />
              </l-popup>
            </l-marker>
           </l-map>
         </div>
       </div>
       <div class="col-12 d-block d-md-none divider-column" id="divider">
         <p v-if="listShown">
           <a href="#food-map">zurück zur Karte</a>
         </p>
         <p v-else>
           <a href="#food-list">zur Liste</a>
         </p>
       </div>
       <div class="col-md-4 order-md-1 sidebar-column">
         <div class="sidebar" id="food-list" v-scroll="handleSidebarScroll">
           <food-sidebar-item v-for="data in facilities" :key="data.ident" :data="data"></food-sidebar-item>
         </div>
       </div>
     </div>
   </div>
</template>

<script>
/* global L */

import 'whatwg-fetch'
import Vue from 'vue'

import { LMap, LTileLayer, LControlZoom, LMarker, LPopup, LTooltip } from 'vue2-leaflet'
import 'leaflet.icon.glyph'

import FoodPopup from './food-popup'
import FoodSidebarItem from './food-sidebar-item'

var getIdFromPopup = (e) => {
  let node = e.popup._content.firstChild
  return node.id.split('-').slice(1).join('-')
}

Vue.directive('scroll', {
  inserted: function (el, binding) {
    let f = function (evt) {
      if (binding.value(evt, el)) {
        window.removeEventListener('scroll', f)
      }
    }
    window.addEventListener('scroll', f)
  }
})

export default {
  name: 'food-map',
  props: ['config'],
  components: { LMap, LTileLayer, LControlZoom, LMarker, LPopup, LTooltip, FoodPopup, FoodSidebarItem
  },
  data () {
    let zoom = null
    let center = null
    if (window.localStorage) {
      zoom = parseInt(window.localStorage.getItem('froide-food:zoom'))
      center = JSON.parse(window.localStorage.getItem('froide-food:center'))
    }

    return {
      zoom: zoom || 12,
      center: center || [
        this.config.city.latitude || 52.518611,
        this.config.city.longitude || 13.408333
      ],
      facilityMap: {},
      facilities: [],
      isMobile: this.detectMobile(),
      listShown: false,
      query: '',
      mapMoved: false,
      tileProvider: {
        name: 'Carto',
        url: '//cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      }
    }
  },
  mounted () {
    this.map.attributionControl.setPrefix('')
    this.map.on('zoomend', (e) => {
      this.mapMoved = true
      this.recordMapPosition()
    })
    this.map.on('moveend', (e) => {
      this.mapMoved = true
      this.recordMapPosition()
    })
    this.map.on('resize', (e) => {
      this.isMobile = this.detectMobile()
    })
    this.map.on('popupopen', (e) => {
      let nodeId = getIdFromPopup(e)
      Vue.set(this.facilities, this.facilityMap[nodeId], {
        ...this.facilities[this.facilityMap[nodeId]],
        sidebarHighlight: true
      })
      let sidebarId = 'sidebar-' + nodeId
      let sidebarItem = document.getElementById(sidebarId)
      if (sidebarItem && sidebarItem.scrollIntoView) {
        sidebarItem.scrollIntoView({behavior: 'smooth'})
      }
    })
    this.map.on('popupclose', (e) => {
      let nodeId = getIdFromPopup(e)
      Vue.set(this.facilities, this.facilityMap[nodeId], {
        ...this.facilities[this.facilityMap[nodeId]],
        sidebarHighlight: false
      })
    })
    this.search()
  },
  computed: {
    map () {
      return this.$refs.map.mapObject
    },
    iconRequested () {
      return window.L.Icon.Default.imagePath + '/markers-request.png'
    },
    iconUnRequested () {
      return window.L.Icon.Default.imagePath + '/glyph-marker-icon.png'
    },
    mapOptions () {
      return {
        scrollWheelZoom: this.isMobile
      }
    },
    topToolsHeight () {
      let height = document.getElementById('searchbar').getBoundingClientRect().height
      return height
    },
    popupOptions () {
      return {
        autoPanPaddingTopLeft: L.point([5, 85]),
        maxWidth: Math.round(window.innerWidth * 0.7)
      }
    }
  },
  methods: {
    search () {
      this.mapMoved = false
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
      let categories = ['restaurants']
      let cats = categories.map((c) => `categories=${encodeURIComponent(c)}`)
      cats = cats.join('&')
      window.fetch(`/api/v1/venue/?lat=${latlng.lat}&lng=${latlng.lng}&radius=${radius}&q=${encodeURIComponent(this.query)}&${cats}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          this.facilityMap = {}
          this.facilities = data.map((r, i) => {
            let d = {
              position: [r.lat, r.lng],
              icon: L.icon.glyph({
                prefix: 'fa',
                glyph: r.request_url ? 'check' : 'cutlery',
                iconUrl: r.request_url ? this.iconRequested : this.iconUnRequested
              }),
              id: r.ident.replace(/:/g, '-'),
              sidebarHighlight: false,
              ...r
            }
            this.facilityMap[d.id] = i
            return d
          })
        })
    },
    handleSidebarScroll (evt, el) {
      let listTop = el.getBoundingClientRect().top
      if (listTop < this.topToolsHeight) {
        this.listShown = true
      } else {
        this.listShown = false
      }
    },
    recordMapPosition () {
      let latlng = this.map.getCenter()
      let zoom = this.map.getZoom()
      if (!window.localStorage) {
        return
      }
      window.localStorage.setItem('froide-food:zoom', zoom)
      window.localStorage.setItem('froide-food:center', JSON.stringify(latlng))
    },
    detectMobile () {
      return window.innerWidth > 768
    }
  }
}
</script>

<style lang="scss" scoped>

.searchbar {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 2050;
  background-color: #fff;
  padding: 0.25rem 0;
}

.map-column {
  position: -webkit-sticky;
  position: sticky;
  top: 50px;
}

.map-container {
  width: 100%;
  height: 40vh;
  position: relative;
}

.sidebar-column {
  transform: translate3d(0px, 0px, 0px);
  z-index: 2020;
  margin-top: -1px;
}

.sidebar {
  background-color: #fff;
}

@media screen and (min-width: 768px){
  .map-container {
    height: 80vh;
  }
  .sidebar {
    height: 80vh;
    overflow-y: scroll;
  }
}
//
// .noScroll {
//   overflow-y: hidden;
// }

.redo-search {
  position: absolute;
  top: 0;
  z-index: 2000;
  width: 50%;
  text-align: center;
  left: 25%;
  button {
    margin-top: 0.5rem;
  }
}

.divider-column {
  background-color: #fff;
  padding: 0.5rem 0;
  z-index: 2025;
  position: -webkit-sticky;
  position: sticky;
  top: 45px;
  text-align: center;

  p {
    margin: 0;
  }
}


</style>
