<template>
  <div class="container-fluid food-map-container">
    <div class="searchbar" id="searchbar">
      <div class="input-group">
        <input type="text" v-model="query" class="form-control" placeholder="Name"  @keydown.enter.prevent="userSearch">
        <div class="input-group-append">
          <button class="btn btn-outline-secondary" type="button" @click="userSearch">
            Suchen
          </button>
        </div>
        <div class="input-group-append">
          <button class="btn btn-outline-secondary" @click="showLocator = true">
            <i class="fa fa-location-arrow" aria-hidden="true"></i>
            <span class="d-none d-sm-none d-md-inline">PLZ</span>
          </button>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-8 order-md-2 map-column">
        <div class="map-container" id="food-map">
          <div v-if="mapMoved" class="redo-search">
            <button class="btn btn-secondary btn-sm" @click="searchArea">
              Im aktuellen Bereich suchen
            </button>
          </div>

          <l-map ref="map" :zoom="zoom" :center="center" :options="mapOptions" :maxBounds="maxBounds">
            <l-tile-layer
              layerType="base" :name="tileProvider.name" :visible="true"
              :url="tileProvider.url" :attribution="tileProvider.attribution"/>

            <l-marker v-for="marker in facilities" :key="marker.ident" :lat-lng="marker.position" :title="marker.name" :draggable="false" :icon="marker.icon">
              <l-tooltip :content="marker.name" />
              <l-popup :options="popupOptions" v-if="!isMobile">
                <food-popup :data="marker" />
              </l-popup>
            </l-marker>
           </l-map>
         </div>
       </div>
       <div class="col-12 d-block d-md-none divider-column" id="divider">
         <p v-if="listShown" class="divider-button">
           <a @click.prevent="goToMap">zurück zur Karte</a>
         </p>
         <p v-else class="divider-button">
           <a href="#food-list">zur Liste</a>
         </p>
       </div>
       <div class="col-md-4 order-md-1 sidebar-column">
         <div class="sidebar" id="food-list" v-scroll="handleSidebarScroll">
           <food-sidebar-item v-for="data in facilities" :key="data.ident" :data="data"></food-sidebar-item>
         </div>
       </div>
     </div>

     <food-locator v-if="showLocator" :defaultPostcode="postcode" @close="showLocator = false" @postcodeChosen="postcodeChosen" @locationChosen="locationChosen"></food-locator>

   </div>
</template>

<script>
/* global L */

import 'whatwg-fetch'
import Vue from 'vue'

import { LMap, LTileLayer, LControlZoom, LMarker, LPopup, LTooltip } from 'vue2-leaflet'
import 'leaflet.icon.glyph'
import bbox from '@turf/bbox'

import FoodPopup from './food-popup'
import FoodSidebarItem from './food-sidebar-item'
import FoodLocator from './food-locator'

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

const GERMANY_BOUNDS = [
  [56.9449741808516, 24.609375000000004],
  [44.402391829093915, -3.5156250000000004]
]
const DETAIL_ZOOM_LEVEL = 12

export default {
  name: 'food-map',
  props: ['config'],
  components: { LMap, LTileLayer, LControlZoom, LMarker, LPopup, LTooltip, FoodPopup, FoodSidebarItem, FoodLocator
  },
  data () {
    let locationKnown = false

    let zoom = null
    let center = null
    let postcode = null

    if (window.localStorage) {
      zoom = parseInt(window.localStorage.getItem('froide-food:zoom'))
      center = JSON.parse(window.localStorage.getItem('froide-food:center'))
      postcode = JSON.parse(window.localStorage.getItem('froide-food:postcode'))
    }
    if (zoom) {
      locationKnown = true
    }

    return {
      zoom: zoom || 6,
      locationKnown: locationKnown,
      showLocator: false,
      maxBounds: L.latLngBounds(GERMANY_BOUNDS),
      postcode: '' + (postcode || this.config.city.postcode || ''),
      center: center || [
        this.config.city.latitude || 51.00289959043832,
        this.config.city.longitude || 10.245523452758789
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
    console.log(L.latLngBounds(GERMANY_BOUNDS))
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
    if (!this.locationKnown) {
      this.showLocator = true
    } else {
      this.search()
    }
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
        scrollWheelZoom: !this.isMobile
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
    locationChosen (latlng) {
      let center = L.latLng(latlng)
      this.map.flyTo(center, DETAIL_ZOOM_LEVEL)
      this.search(center)
      this.map.on('zoomend', this.preventMapMoved)
    },
    postcodeChosen (postcode) {
      window.localStorage.setItem('froide-food:postcode', postcode)
      window.fetch(`/api/v1/georegion/?kind=zipcode&name=${postcode}&limit=1`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          if (data['meta']['total_count'] === 0) {
            return
          }
          let geoRegion = data.objects[0]
          let bounds = bbox(geoRegion.geom)
          bounds = L.latLngBounds([
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]]
          ])
          let coords = geoRegion.centroid.coordinates
          let center = L.latLng([coords[1], coords[0]])
          this.map.flyToBounds(bounds)
          this.search(center, bounds)
          this.map.on('zoomend', this.preventMapMoved)
        })
    },
    preventMapMoved () {
      window.requestAnimationFrame(() => {
        this.mapMoved = false
      })
      this.map.off('zoomend', this.preventMapMoved)
    },
    userSearch () {
      if (this.query.match(/^\d{5}$/)) {
        let p = this.query
        this.query = ''
        return this.postcodeChosen(p)
      }
      this.search()
    },
    searchArea () {
      this.search()
      this.mapMoved = false
    },
    search (latlng, bounds) {
      if (!latlng) {
        latlng = this.map.getCenter()
      }
      if (!bounds) {
        bounds = this.map.getBounds()
      }
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
    goToMap () {
      window.scrollTo(0, 0)
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
      return window.innerWidth <= 768
    }
  }
}
</script>

<style lang="scss" scoped>

.food-map-container {
  padding-bottom: 1rem;
}

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

  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px){
  .map-column {
    padding-right: 15px;
    padding-left: 15px;
  }
}

.map-container {
  width: 100%;
  height: 50vh;
  position: relative;
}

.sidebar-column {
  transform: translate3d(0px, 0px, 0px);
  z-index: 2020;
  margin-top: -1px;
  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px){
  .sidebar-column {
    padding-right: 15px;
    padding-left: 15px;
  }
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
  padding: 0.25rem 0;
  z-index: 2025;
  position: -webkit-sticky;
  position: sticky;
  top: 45px;
  text-align: center;
}
.divider-button {
  margin: 0;
  a {
    padding: 0.25rem 0.5rem;
    background: #eee;
    color: #333;
    border-radius: 5px;
  }
}



</style>
