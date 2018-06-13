<template>
  <div :class="{'food-map-embed': config.embed}" v-scroll="handleSidebarScroll">
    <div class="food-map-container container-fluid" id="food-map-container" :class="{'is-embed': config.embed}">
      <div class="searchbar" id="searchbar">
        <div class="searchbar-inner">
          <div class="input-group">
            <input type="text" v-model="query" class="form-control" placeholder="Name"  @keydown.enter.prevent="userSearch">
            <div class="input-group-append">
              <button class="btn btn-outline-secondary" type="button" @click="userSearch">
                <i class="fa fa-search" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Suchen</span>
              </button>
            </div>
            <div class="input-group-append mr-auto">
              <button class="btn btn-outline-secondary" @click="showLocator = true">
                <i class="fa fa-location-arrow" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">PLZ</span>
              </button>
            </div>
            <div class="input-group-append" v-if="false">
              <button class="btn btn-outline-secondary" :class="{'active': showFilter}" @click="openFilter">
                <i class="fa fa-gears" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Filter</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      <slide-up-down :active="showFilter" :duration="300">
        <food-filter :filters="filters" @change="filterChanged" @apply="applyFilter"></food-filter>
      </slide-up-down>
      <div class="row">
        <div class="col-md-7 col-lg-8 order-md-2 map-column">
          <div class="map-container" id="food-map">
            <div v-if="showRefresh || searching" class="redo-search">
              <button v-if="showRefresh" class="btn btn-secondary btn-sm" @click="searchArea">
                Im aktuellen Bereich suchen
              </button>
              <button v-if="searching" class="btn btn-secondary btn-sm disabled">
                <food-loader></food-loader>
                Suche läuft&hellip;
              </button>
            </div>

            <l-map ref="map" :zoom="zoom" :center="center" :options="mapOptions" :maxBounds="maxBounds">
              <l-tile-layer
                layerType="base" :name="tileProvider.name" :visible="true"
                :url="tileProvider.url" :attribution="tileProvider.attribution"/>

              <l-marker v-for="marker in facilities" :key="marker.id" :lat-lng="marker.position" :title="marker.name" :draggable="false" :icon="marker.icon" :options="markerOptions"
              @click="markerClick(marker)"
              @touchstart.prevent="markerClick(marker)" v-focusmarker>
                <l-tooltip :content="marker.name" v-if="!isMobile"/>
                <l-popup :options="popupOptions" v-if="!isMobile">
                  <food-popup :data="marker" :config="config" />
                </l-popup>
              </l-marker>
            </l-map>
            <food-mapoverlay :data="selectedFacility" :config="config" v-if="isMobile && selectedFacility" @close="clearSelected"></food-mapoverlay>
          </div>
        </div>

        <div class="col-12 d-block d-md-none divider-column" id="divider">
          <p v-if="listShown" class="divider-button">
            <a @click.prevent="goToMap" @touchstart.prevent="goToMap">zurück zur Karte</a>
          </p>
          <p v-else class="divider-button">
            <a @click.prevent="goToList" @touchstart.prevent="goToList">zur Liste</a>
          </p>
        </div>

        <div class="col-md-5 col-lg-4 order-md-1 sidebar-column">
          <div class="sidebar" id="food-list" v-scroll.window="handleSidebarScroll">
            <div v-if="searching" class="loader"></div>
            <food-sidebar-item v-else v-for="data in facilities"
                :key="data.ident" :data="data"
                :config="config"
                :selectedFacilityId="selectedFacilityId"
                @select="markerClick(data)"></food-sidebar-item>
          </div>
        </div>

      </div>

      <food-locator v-if="showLocator" :defaultPostcode="postcode" @close="showLocator = false" @postcodeChosen="postcodeChosen" @locationChosen="locationChosen"></food-locator>

    </div>
  </div>
</template>

<script>
/* global L */

import 'whatwg-fetch'
import Vue from 'vue'

import { LMap, LTileLayer, LControlZoom, LMarker, LPopup, LTooltip } from 'vue2-leaflet'
import 'leaflet.icon.glyph'
import bbox from '@turf/bbox'
import smoothScroll from '../lib/smoothscroll'
import SlideUpDown from 'vue-slide-up-down'

import FoodPopup from './food-popup'
import FoodSidebarItem from './food-sidebar-item'
import FoodLocator from './food-locator'
import FoodMapoverlay from './food-mapoverlay'
import FoodFilter from './food-filter'
import FoodLoader from './food-loader'

var getIdFromPopup = (e) => {
  let node = e.popup._content.firstChild
  return node.id.split('-').slice(1).join('-')
}

Vue.directive('scroll', {
  inserted: function (el, binding) {
    let scrollElement = el
    if (binding.modifiers.window) {
      scrollElement = window
    }
    let f = function (evt) {
      if (binding.value(evt, el)) {
        scrollElement.removeEventListener('scroll', f)
      }
    }
    scrollElement.addEventListener('scroll', f)
  }
})

const GERMANY_BOUNDS = [
  [56.9449741808516, 24.609375000000004],
  [44.402391829093915, -3.5156250000000004]
]
const DETAIL_ZOOM_LEVEL = 12
const DEFAULT_ZOOM = 6

export default {
  name: 'food-map',
  props: ['config'],
  components: { LMap, LTileLayer, LControlZoom, LMarker, LPopup, LTooltip, FoodPopup, FoodSidebarItem, FoodLocator, FoodMapoverlay, FoodFilter, FoodLoader, SlideUpDown
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
    if (zoom && zoom !== DEFAULT_ZOOM) {
      locationKnown = true
    }

    return {
      zoom: zoom || (this.config.city.latitude ? DETAIL_ZOOM_LEVEL : DEFAULT_ZOOM),
      locationKnown: locationKnown,
      showLocator: false,
      showFilter: false,
      filters: this.config.filters,
      maxBounds: L.latLngBounds(GERMANY_BOUNDS),
      postcode: '' + (postcode || this.config.city.postal_code || ''),
      center: center || [
        this.config.city.latitude || 51.00289959043832,
        this.config.city.longitude || 10.245523452758789
      ],
      selectedFacilityId: null,
      facilityMap: {},
      facilities: [],
      searching: false,
      isMobile: L.Browser.mobile || (window.innerWidth < 768),
      listShown: false,
      query: '',
      mapMoved: false,
      tooltipOffset: L.point([-10, -50]),
      markerOptions: {
        riseOnHover: true
      },
      tileProvider: {
        name: 'Carto',
        url: `//cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}${window.L.Browser.retina ? '@2x' : ''}.png`,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      }
    }
  },
  created () {
    var self = this
    Vue.directive('focusmarker', {
      // When the bound element is inserted into the DOM...
      componentUpdated: (el, binding, vnode) => {
        if (vnode.key === self.selectedFacilityId) {
          vnode.componentInstance.mapObject.setZIndexOffset(300)
        } else {
          vnode.componentInstance.mapObject.setZIndexOffset(0)
        }
      }
    })
  },
  mounted () {
    this.map.attributionControl.setPrefix('')
    this.map.on('zoomend', (e) => {
      this.mapMoved = true
      this.zoom = this.map.getZoom()
      this.recordMapPosition()
    })
    this.map.on('moveend', (e) => {
      this.mapMoved = true
      this.recordMapPosition()
    })
    this.map.on('click', (e) => {
      this.clearSelected()
    })
    this.map.on('popupopen', (e) => {
      let nodeId = getIdFromPopup(e)
      this.selectedFacilityId = nodeId
      let sidebarId = 'sidebar-' + nodeId
      let sidebarItem = document.getElementById(sidebarId)
      if (sidebarItem && sidebarItem.scrollIntoView) {
        sidebarItem.scrollIntoView({behavior: 'smooth'})
      }
    })
    this.map.on('popupclose', (e) => {
      this.clearSelected()
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
    iconUnRequested () {
      return this.config.imagePath + '/pin_0.svg'
    },
    iconRequested () {
      return this.config.imagePath + '/pin_1.svg'
    },
    iconSelectedUnRequested () {
      return this.config.imagePath + '/pin_0_1.svg'
    },
    iconSelectedRequested () {
      return this.config.imagePath + '/pin_1_1.svg'
    },
    iconCategoryMapping () {
      let filterIconMapping = {}
      this.filters.forEach((f) => {
        f.categories.forEach((c) => {
          filterIconMapping[c] = f.icon
        })
      })
      return filterIconMapping
    },
    filterCategories () {
      let filterCats = []
      this.filters.forEach((f) => {
        if (f.active) {
          filterCats = filterCats.concat(f.categories)
        }
      })
      if (filterCats.length === 0) {
        this.filters.forEach((f) => {
          filterCats = filterCats.concat(f.categories)
        })
      }
      return filterCats
    },
    mapOptions () {
      return {
        scrollWheelZoom: !this.isMobile
      }
    },
    dividerSwitchHeight () {
      return window.innerHeight / 2
    },
    selectedFacility () {
      if (this.selectedFacilityId) {
        return this.facilities[this.facilityMap[this.selectedFacilityId]]
      }
      return null
    },
    popupOptions () {
      return {
        autoPanPaddingTopLeft: L.point([5, 85]),
        maxWidth: Math.round(window.innerWidth * 0.7)
      }
    },
    showRefresh () {
      return this.mapMoved && this.zoom >= 10
    },
    scrollContainer () {
      return this.config.embed ? document.querySelector('.food-map-embed') : document.documentElement
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
    filterChanged (filter) {
      this.filters = this.filters.map((f) => {
        if (f.name === filter.name) {
          f.active = !f.active
        }
        return f
      })
    },
    applyFilter () {
      this.showFilter = false
      this.search()
    },
    openFilter () {
      this.showFilter = !this.showFilter
      if (this.isMobile) {
        this.goToMap()
      }
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
    },
    search (latlng, bounds) {
      this.mapMoved = false
      this.searching = true
      this.clearSelected()
      this.facilities = []
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
      let categories = this.filterCategories
      let cats = categories.map((c) => `categories=${encodeURIComponent(c)}`)
      cats = cats.join('&')
      window.fetch(`/api/v1/venue/?lat=${latlng.lat}&lng=${latlng.lng}&radius=${radius}&q=${encodeURIComponent(this.query)}&${cats}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          if (data.error) {
            console.warn('Error requesting the API')
          }
          this.searching = false
          this.facilityMap = {}
          this.facilities = data.results.map((r, i) => {
            let d = {
              position: [r.lat, r.lng],
              id: r.ident.replace(/:/g, '-'),
              ...r
            }
            d.icon = this.getIcon(d)
            this.facilityMap[d.id] = i
            return d
          })
        })
    },
    getIcon (r) {
      let iconUrl = r.request_url ? this.iconRequested : this.iconUnRequested
      if (this.selectedFacilityId === r.id) {
        iconUrl = r.request_url ? this.iconSelectedRequested : this.iconSelectedUnRequested
      }
      return L.icon.glyph({
        className: 'food-marker-icon ',
        prefix: 'fa',
        glyph: this.iconCategoryMapping[r.category] || 'question',
        iconUrl: iconUrl
      })
    },
    clearSelected () {
      if (this.selectedFacilityId === null) {
        return
      }
      let marker = this.facilities[this.facilityMap[this.selectedFacilityId]]
      this.selectedFacilityId = null
      if (marker) {
        Vue.set(marker, 'icon', this.getIcon(marker))
      }
    },
    markerClick (marker) {
      this.clearSelected()
      this.map.panTo(marker.position)
      this.selectedFacilityId = marker.id
      Vue.set(marker, 'icon', this.getIcon(marker))
    },
    goToMap () {
      let y = document.getElementById('food-map-container').offsetTop
      smoothScroll({x: 0, y: y, el: this.scrollContainer}, 300)
    },
    goToList () {
      let y = document.getElementById('food-map-container').offsetTop
      let y2 = document.getElementById('food-map').getBoundingClientRect().height
      smoothScroll({x: 0, y: y + y2 + 2, el: this.scrollContainer}, 300)
    },
    handleSidebarScroll (evt, el) {
      let listTop = document.getElementById('food-list').getBoundingClientRect().top
      if (listTop < this.dividerSwitchHeight) {
        if (!this.listShown) {
          this.showFilter = false
        }
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
    }
  }
}
</script>

<style lang="scss" scoped>

.food-map-embed {
  border: 1px solid #eee;
  padding: 0 10px 10px;
  height: 100vh;
  overflow: scroll;
}

@media screen and (min-width: 768px){
  .food-map-embed {
    padding: 0;
  }
}

.food-map-container {
  padding-bottom: 1rem;
}

.searchbar {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 2050;
  background-color: #fff;
  margin:0 -15px;
}

.searchbar-inner {
  padding: 0;
}

@media screen and (min-width: 768px){
  .searchbar-inner {
    padding: 0 15px;
  }
}

.map-column {
  position: -webkit-sticky;
  position: sticky;
  top: 38px;

  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px){
  .map-column {
    padding-right: 15px;
    padding-left: 5px;
  }
}

.map-container {
  width: 100%;
  height: 50vh;
  position: relative;
  overflow: hidden;
}
.sidebar {
  background-color: #fff;
}

@media screen and (min-width: 768px){
  .map-container {
    height: 80vh;
  }
  .is-embed .map-container {
    height: 90vh;
  }
  .sidebar {
    height: 80vh;
    overflow-y: scroll;
  }
  .is-embed .sidebar {
    height: 90vh;
  }
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
    padding-right: 0px;
    padding-left: 15px;
  }
}


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
  border-bottom: 2px solid #eee;
  padding: 0.25rem 0;
  z-index: 2025;
  position: -webkit-sticky;
  position: sticky;
  top: 37px;
  padding: 8px 0 8px;
  text-align: center;
  cursor: pointer;
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

.is-embed {
  .searchbar {
    padding: 15px 0 0;
  }
  .map-column {
    top: 53px;
  }
  .divider-column {
    top: 52px;
  }
}

</style>
