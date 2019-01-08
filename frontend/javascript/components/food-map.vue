<template>
  <div>
    <food-request v-if="showRequestForm"
      :config="requestConfig"
      :request-form="requestForm"
      :user-info="userInfo"
      :user-form="userForm"
      :data="showRequestForm"
      :current-url="currentUrl"
      @detailfetched="detailFetched"
      @close="requestFormClosed"
    ></food-request>
    <div v-show="!showRequestForm" :class="{'food-map-embed': config.embed, 'modal-active': modalActive}" v-scroll="handleSidebarScroll">
      <div class="food-map-container container-fluid" ref="foodMapContainer" id="food-map-container" :class="{'is-embed': config.embed}">

        <div class="searchbar d-block d-md-none" id="searchbar">
          <div class="searchbar-inner">
            <div class="input-group">
              <div class="clearable-input">
                <input type="text" v-model="query" class="form-control" placeholder="Suche nach Restaurant etc." @keydown.enter.prevent="userSearch">
                <span class="clearer fa fa-close" v-if="query.length > 0" @click="clearSearch"></span>
              </div>
              <div class="input-group-append">
                <button class="btn btn-outline-secondary" type="button" @click="userSearch">
                  <i class="fa fa-search" aria-hidden="true"></i>
                  <span class="d-none d-sm-none d-md-inline">Suchen</span>
                </button>
              </div>
              <div class="input-group-append mr-auto">
                <button class="btn btn-outline-secondary" @click="setLocator(true)">
                  <i class="fa fa-location-arrow" aria-hidden="true"></i>
                  <span class="d-none d-sm-none d-md-inline">Ort</span>
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
        <!-- <slide-up-down :active="showFilter" :duration="300">
          <food-filter :filters="filters" @change="filterChanged" @apply="applyFilter"></food-filter>
        </slide-up-down> -->
        <div class="row">
          <div class="col-md-7 col-lg-8 order-md-2 map-column">
            <div class="map-container" ref="foodMap" id="food-map" :class="mapContainerClass" :style="mapContainerStyle">

              <div v-if="showRefresh || searching" class="redo-search">
                <button v-if="showRefresh" class="btn btn-dark" @click="searchArea">
                  Im aktuellen Bereich suchen
                </button>
                <button v-if="searching" class="btn btn-secondary btn-sm disabled">
                  <food-loader></food-loader>
                  Suche läuft&hellip;
                </button>
              </div>

              <div class="map-search d-none d-md-block">
                <div class="input-group">
                  <div class="clearable-input">
                    <input type="text" v-model="query" class="form-control" placeholder="Suche Restaurant"  @keydown.enter.prevent="userSearch">
                    <span class="clearer fa fa-close" v-if="query.length > 0" @click="clearSearch"></span>
                  </div>
                  <div class="input-group-append">
                    <button class="btn btn-outline-secondary" type="button" @click="userSearch">
                      <i class="fa fa-search" aria-hidden="true"></i>
                      <span class="d-none d-sm-none d-lg-inline">Suchen</span>
                    </button>
                  </div>
                  <div class="input-group-append">
                    <button class="btn btn-outline-secondary" @click="setLocator(true)">
                      <i class="fa fa-location-arrow" aria-hidden="true"></i>
                      <span class="d-none d-lg-inline">Ort</span>
                    </button>
                  </div>
                </div>
              </div>

              <l-map ref="map" :zoom="zoom" :center="center" :options="mapOptions" :maxBounds="maxBounds">
                <l-tile-layer
                  layerType="base" :name="tileProvider.name" :visible="true"
                  :url="tileProvider.url" :attribution="tileProvider.attribution"/>

                <l-control-zoom position="bottomright" v-if="!isTouch"/>

                <l-marker v-for="marker in venues" :key="marker.id"
                    :lat-lng="marker.position" :title="marker.name"
                    :draggable="false" :icon="marker.icon" :options="markerOptions"
                    @click="markerClick(marker, false)"
                    @touchstart.prevent="markerClick(marker, false)" v-focusmarker>
                  <l-tooltip :content="marker.name" :options="tooltipOptions" v-if="!isMobile"/>
                  <l-popup :options="popupOptions" v-if="!isMobile">
                    <food-popup
                      :data="marker"
                      :config="config"
                      @startRequest="startRequest"
                      @detail="setDetail"/>
                  </l-popup>
                </l-marker>

              </l-map>
              <food-mapoverlay v-if="stacked && selectedVenue"
                :data="selectedVenue"
                :config="config"
                @close="clearSelected"
                @startRequest="startRequest"
                @detail="setDetail"
              ></food-mapoverlay>
            </div>
          </div>

          <div class="col-12 d-block d-md-none divider-column" id="divider">
            <p v-if="listShown" class="divider-button">
              <a @click.prevent="goToMap" @touchend.prevent="goToMap">zurück zur Karte</a>
            </p>
            <p v-else class="divider-button">
              <a @click.prevent="goToList" @touchend.prevent="goToList">zur Liste</a>
            </p>
          </div>

          <div class="col-md-5 col-lg-4 order-md-1 sidebar-column">
            <div class="sidebar" :class="{'modal-active': modalActive}" ref="foodList" id="food-list" v-scroll.window="handleSidebarScroll">
              <food-sidebar-item v-if="searching" v-for="data in fakeVenues"
                :key="data.id"
                :data="data">
              </food-sidebar-item>
              <food-sidebar-item v-for="data in venues"
                  :key="data.ident" :data="data"
                  :config="config"
                  :selectedVenueId="selectedVenueId"
                  @select="markerClick(data, true)"
                  @detail="setDetail"
                  @startRequest="startRequest"
                  @imageLoaded="imageLoaded"></food-sidebar-item>
            </div>
          </div>

        </div>
        <food-locator v-if="showLocator"
          :defaultPostcode="postcode"
          :defaultLocation="locationName"
          :exampleCity="city"
          :locationKnown="locationKnown"
          :error="error"
          :isMobile="isMobile"
          @close="setLocator(false)"
          @postcodeChosen="postcodeChosen"
          @coordinatesChosen="coordinatesChosen"
          @locationChosen="locationChosen"
          ></food-locator>
        <food-detail v-if="showDetail"
          :data="showDetail"
          @close="showDetail = null"
          @detailfetched="detailFetched"
        ></food-detail>
      </div>
    </div>
  </div>
</template>

<script>
/* global L */

import 'whatwg-fetch'
import Vue from 'vue'

import { LMap, LTileLayer, LControlLayers, LControlZoom, LMarker, LPopup, LTooltip } from 'vue2-leaflet'
import 'leaflet.icon.glyph'
import bbox from '@turf/bbox'
import smoothScroll from '../lib/smoothscroll'
import SlideUpDown from 'vue-slide-up-down'

import FoodPopup from './food-popup'
import FoodSidebarItem from './food-sidebar-item'
import FoodLocator from './food-locator'
import FoodMapoverlay from './food-mapoverlay'
import FoodFilter from './food-filter'
import FoodDetail from './food-detail'
import FoodLoader from './food-loader'
import FoodRequest from './food-request'

import {
  getPlaceStatus, getPinURL, getPinColor,
  getQueryVariable, canUseLocalStorage, latlngToGrid
} from '../lib/utils'

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
const DEFAULT_POS = [51.00289959043832, 10.245523452758789]

export default {
  name: 'food-map',
  props: {
    config: {
      type: Object
    },
    userInfo: {
      type: Object,
      default: null
    },
    userForm: {
      type: Object,
      default: null
    },
    requestForm: {
      type: Object
    },
    requestConfig: {
      type: Object
    }
  },
  components: {
    LMap, LTileLayer, LControlLayers, LControlZoom, LMarker, LPopup, LTooltip,
    FoodPopup, FoodSidebarItem, FoodLocator, FoodMapoverlay, FoodLoader, FoodDetail,
    FoodFilter, FoodRequest, SlideUpDown
  },
  data () {
    let locationKnown = false

    let zoom = null
    let center = null
    let postcode = null
    let requestsMade = []

    let latlng = getQueryVariable('latlng')
    let query = getQueryVariable('query')
    let paramIdent = getQueryVariable('ident')

    let city = this.config.city
    if (city.country_code && city.country_code !== 'DE') {
      city = {}
    }

    if (latlng) {
      let parts = latlng.split(',')
      center = [
        parseFloat(parts[0]),
        parseFloat(parts[1])
      ]
      if (center[0] && center[1]) {
        zoom = DETAIL_ZOOM_LEVEL
      }
    }

    if (canUseLocalStorage(window)) {
      requestsMade = JSON.parse(window.localStorage.getItem('froide-food:requestsmade'))
      zoom = parseInt(window.localStorage.getItem('froide-food:zoom'))
      if (center === null) {
        center = JSON.parse(window.localStorage.getItem('froide-food:center'))
        if (center !== null) {
          center = [center.lat, center.lng]
        }
      }
      postcode = JSON.parse(window.localStorage.getItem('froide-food:postcode'))
    }
    if (center === null) {
      center = [null, null]
    }

    center = [
      center[0] || city.latitude || DEFAULT_POS[0],
      center[1] || city.longitude || DEFAULT_POS[1]
    ]

    if (center[0] !== DEFAULT_POS[0]) {
      locationKnown = true
      zoom = zoom || DETAIL_ZOOM_LEVEL
    } else {
      zoom = DEFAULT_ZOOM
    }

    return {
      zoom: zoom,
      locationKnown: locationKnown,
      showLocator: false,
      showFilter: false,
      showDetail: null,
      showRequestForm: null,
      filters: this.config.filters,
      maxBounds: L.latLngBounds(GERMANY_BOUNDS),
      city: city.city,
      postcode: '' + (postcode || city.postal_code || ''),
      locationName: '',
      center: center,
      requestsMade: requestsMade,
      selectedVenueId: null,
      venueMap: {},
      venues: [],
      searching: false,
      error: false,
      stacked: this.isStacked(),
      isMapTop: false,
      mapHeight: null,
      isTouch: L.Browser.touch && L.Browser.mobile,
      listShown: false,
      query: query || '',
      paramIdent: paramIdent,
      mapMoved: false,
      autoMoved: false,
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

    if ('serviceWorker' in navigator) {
      let scope = this.config.swUrl.replace(/^(.*\/)[\w\.]+$/, '$1')
      navigator.serviceWorker.register(this.config.swUrl, {scope: scope}).then(function(reg) {
        console.log('ServiceWorker registration successful!', reg.scope);
      }).catch(function(err) {
        console.log('ServiceWorker registration failed: ', err);
      });
    }

    Vue.directive('focusmarker', {
      // When the bound element is inserted into the DOM...
      componentUpdated: (el, binding, vnode) => {
        if (vnode.key === self.selectedVenueId) {
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
      this.mapHasMoved()
      this.zoom = this.map.getZoom()
      this.recordMapPosition()
    })
    this.map.on('moveend', (e) => {
      this.mapHasMoved()
      this.recordMapPosition()
    })
    this.map.on('click', (e) => {
      this.clearSelected()
    })
    this.map.on('popupopen', (e) => {
      let nodeId = getIdFromPopup(e)
      this.selectedVenueId = nodeId
    })
    this.map.on('popupclose', (e) => {
      this.clearSelected()
    })
    window.addEventListener('resize', () => {
      this.isStacked()
    })
    if (!this.locationKnown) {
      this.setLocator(true)
    } else {
      this.search()
    }
  },
  computed: {
    map () {
      return this.$refs.map.mapObject
    },
    currentUrl () {
      let url = `${this.config.appUrl}?latlng=${this.center[0]},${this.center[1]}`
      
      if (this.selectedVenueId) {
        url += `&ident=${encodeURIComponent(this.selectedVenue.ident)}`
        url += `&query=${encodeURIComponent(this.selectedVenue.name)}`
      } else if (this.query) {
        url += `&query=${encodeURIComponent(this.query)}`
      }
      return url
    },
    isMobile () {
      return this.stacked || L.Browser.mobile
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
        scrollWheelZoom: !this.isMobile,
        doubleClickZoom: true,
        zoomControl: false,
        maxZoom: 18
      }
    },
    tooltipOptions () {
      return {
        offset: L.point(0, -40),
        direction: 'top'
      }
    },
    dividerSwitchHeight () {
      return window.innerHeight / 2
    },
    selectedVenue () {
      if (this.selectedVenueId) {
        return this.venues[this.venueMap[this.selectedVenueId]]
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
      return this.config.embed ? document.querySelector('.food-map-embed') : window
    },
    mapContainerClass () {
      if (this.isMapTop && !this.stacked) {
        return 'map-full-height'
      }
    },
    mapContainerStyle () {
      if (this.mapHeight === null) {
        return ''
      }
      return `height: ${this.mapHeight}px`
    },
    fakeVenues () {
      let a = []
      for (let i = 0; i < 50; i += 1) {
        a.push({id: 'fake-' + i});
      }
      return a
    },
    modalActive () {
      return this.showLocator || this.showDetail
    }
  },
  methods: {
    coordinatesChosen (latlng) {
      let center = L.latLng(latlng)
      this.locationKnown = true
      this.map.setView(center, DETAIL_ZOOM_LEVEL)
      this.search({coordinates: center})
      this.preventMapMoved()
    },
    locationChosen (location) {
      this.locationName = location
      this.search({location: location})
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
          this.locationKnown = true
          let geoRegion = data.objects[0]
          let bounds = bbox(geoRegion.geom)
          bounds = L.latLngBounds([
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]]
          ])
          let coords = geoRegion.centroid.coordinates
          let center = L.latLng([coords[1], coords[0]])
          this.map.fitBounds(bounds)
          this.search({coordinates: center, bounds})
          this.preventMapMoved()
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
    mapHasMoved() {
      if (this.autoMoved) {
        window.requestAnimationFrame(() => {
          this.autoMoved = false
        })
        return
      }
      this.mapMoved = true
    },
    preventMapMoved () {
      this.autoMoved = true
    },
    userSearch () {
      if (this.query.match(/^\d{5}$/)) {
        let p = this.query
        this.query = ''
        return this.postcodeChosen(p)
      }
      this.search()
    },
    clearSearch () {
      this.query = ''
      this.search()
    },
    searchArea () {
      this.search()
    },
    search (options = {}) {
      this.mapMoved = false
      this.error = false
      this.searching = true
      this.clearSelected()
      this.venues = []
      this.goToMap()
      let locationParam
      if (options.location) {
        locationParam = `location=${options.location}`
      } else {
        let coordinates = options.coordinates
        if (!coordinates) {
          coordinates = this.map.getCenter()
        }
        let bounds = options.bounds
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
        radius = Math.max(Math.round(Math.min(radius, 40000) * 100) / 100, 500)
        let reqCoords = latlngToGrid(coordinates, radius)
        locationParam = `lat=${reqCoords.lat}&lng=${reqCoords.lng}&radius=${radius}`
      }
      let categories = this.filterCategories
      let cats = categories.map((c) => `categories=${encodeURIComponent(c)}`)
      cats = cats.join('&')
      window.fetch(`/api/v1/venue/?q=${encodeURIComponent(this.query)}&${cats}&${locationParam}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          if (data.error) {
            console.warn('Error requesting the API')
            this.goToMap()
            this.location = ''
            this.searching = false
            this.error = true
            this.showLocator = true
            return
          }
          this.locationKnown = true
          this.venueMap = {}
          this.venues = data.results.map((r, i) => {
            let d = {
              position: [r.lat, r.lng],
              id: r.ident.replace(/:/g, '-'),
              full: false,
              ...r
            }
            d.icon = this.getIcon(d)
            this.venueMap[d.id] = i
            if (this.paramIdent && r.ident.indexOf(this.paramIdent) !== -1) {
              this.selectedVenueId = d.id
            }
            return d
          })
          if (options.location) {
            let venueLocations = this.venues.map((r) => {
              return L.latLng(r.position[0], r.position[1])
            })
            let bounds = L.latLngBounds(venueLocations)
            this.map.fitBounds(bounds)
          }
          this.preventMapMoved()
          this.searching = false
        })
    },
    getIcon (r) {
      let status = getPlaceStatus(r)
      let selected = this.selectedVenueId === r.id
      let color = getPinColor(status, selected)
      let iconUrl = getPinURL(color)
      return L.icon.glyph({
        className: 'food-marker-icon ',
        prefix: 'fa',
        glyph: this.iconCategoryMapping[r.category] || 'question',
        iconUrl: iconUrl
      })
    },
    clearSelected () {
      if (this.selectedVenueId === null) {
        return
      }
      let marker = this.venues[this.venueMap[this.selectedVenueId]]
      this.selectedVenueId = null
      if (marker) {
        this.map.closePopup()
        Vue.set(marker, 'icon', this.getIcon(marker))
      }
    },
    markerClick (marker, pan) {
      this.clearSelected()
      if (pan) {
        this.map.panTo(marker.position)
      }
      this.selectedVenueId = marker.id
      if (!this.stacked) {
        let sidebarId = 'sidebar-' + marker.id
        let sidebarItem = document.getElementById(sidebarId)
        if (sidebarItem) {
          if (sidebarItem.scrollIntoView) {
            let scrollDifference = Math.abs(sidebarItem.getBoundingClientRect().top - window.pageYOffset)
            sidebarItem.scrollIntoView({behavior: scrollDifference < 2000 ? 'smooth': 'instant', 'block': 'nearest'})
          } else {
            window.scrollTo(0, sidebarItem.offsetTop)
          }
        }
      } else {
        this.goToMap()
      }
      Vue.set(marker, 'icon', this.getIcon(marker))
    },
    imageLoaded (data) {
      Vue.set(data, 'imageLoaded', true)
    },
    goToMap () {
      let fmc = this.$refs.foodMapContainer
      if (fmc.getBoundingClientRect().top > 0) {
        return
      }
      let y = fmc.offsetTop
      smoothScroll({x: 0, y: y, el: this.scrollContainer}, 300)
    },
    goToList () {
      let y = this.$refs.foodMapContainer.offsetTop
      let y2 = this.$refs.foodMap.getBoundingClientRect().height
      smoothScroll({x: 0, y: y + y2 + 5, el: this.scrollContainer}, 300)
    },
    isStacked () {
      return this.stacked = (window.innerWidth < 768)
    },
    handleSidebarScroll (evt, el) {
      if (this.modalActive) {
        return
      }
      if (L.Browser.safari) {
        /* FIXME: Ugly workaround for render bug in latest safari */
        this.$refs.foodMap.style.top = 'unset'
        window.requestAnimationFrame(() => {
          this.$refs.foodMap.style.top = 0
        })
      }
      let listTop = this.$refs.foodList.getBoundingClientRect().top
      if (listTop < this.dividerSwitchHeight) {
        if (!this.listShown) {
          this.showFilter = false
        }
        this.listShown = true
      } else {
        this.listShown = false
      }
      let mapRect = this.$refs.foodMap.getBoundingClientRect()
      let mapTop = mapRect.top
      let isMapTop = mapTop <= 0
      if (isMapTop !== this.isMapTop) {
        window.setTimeout(() => {
          this.map.invalidateSize()
        }, 1000)
        this.preventMapMoved()
      }
      this.isMapTop = isMapTop
      if (!this.stacked) {
        if (!isMapTop) {
          this.mapHeight = window.innerHeight - mapTop
        } else {
          this.mapHeight = null
        }
      }
    },
    recordMapPosition () {
      let latlng = this.map.getCenter()
      this.center = [latlng.lat, latlng.lng]
      let zoom = this.map.getZoom()
      if (!canUseLocalStorage(window)) {
        return
      }
      window.localStorage.setItem('froide-food:zoom', zoom)
      window.localStorage.setItem('froide-food:center', JSON.stringify(latlng))
    },
    setDetail (data) {
      this.showDetail = data
      if (data) {
        this.goToMap()
      }
    },
    setLocator (data) {
      this.showLocator = data
      if (data) {
        this.goToMap()
      }
    },
    startRequest (data) {
      this.markerClick(data, true)
      this.showRequestForm = data
      this.goToMap()
    },
    requestFormClosed () {
      this.showRequestForm = null
      this.goToMap()
    },
    detailFetched (data) {
      this.venues = this.venues.map((f) => {
        if (f.ident === data.ident) {
          f.requests = data.requests
          f.publicbody = data.publicbody
          f.makeRequestURL = data.makeRequestURL
          f.userRequestCount = data.userRequestCount
          f.full = true
          return f
        }
        return f
      })
    }
  }
}
</script>

<style lang="scss" scoped>

$icon-normal: #007bff;
$icon-pending: #ffc107;
$icon-success: #28a745;
$icon-failure: #dc3545;

.icon-normal {
  fill: $icon-normal;
}
.icon-normal.selected {
  fill: darken($icon-normal, 30%)
}

.icon-pending {
  fill: $icon-pending;
}
.icon-pending.selected {
  fill: darken($icon-pending, 30%)
}

.icon-success {
  fill: $icon-normal;
}
.icon-success.selected {
  fill: darken($icon-success, 30%)
}

.icon-failure {
  fill: $icon-failure;
}
.icon-failure.selected {
  fill: darken($icon-failure, 30%)
}

.food-wrapper {
  position: relative;
}

.food-map-embed {
  border: 1px solid #eee;
  padding: 0 10px 10px;
  height: 100vh;
  overflow: scroll;

  &.modal-active {
    overflow: hidden;  
  }
}

@media screen and (min-width: 768px){
  .food-map-embed {
    padding: 0;
  }
}

.food-map-container {
  position: relative;
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

.map-search {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 2000;
  width: 50%;
  margin-top: 1rem;
  margin-right: 1rem;

  .btn {
    background-color: #fff;
  }
  .btn:hover, .btn:active {
    background-color: #666;
  }
}

@media screen and (max-width: 960px){
  .map-search {
    width: 40%;
  }
}

.redo-search {
  position: absolute;
  z-index: 2000;
  width: auto;

  top: 0;
  left: 0;
  right: 0;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  margin-top: 1rem;

  pointer-events: none;
  .btn {
    pointer-events: auto;
  }
}

@media screen and (min-width: 768px){
  .redo-search {
    left: 0;
    width: 40%;
    text-align: left;
    margin-left: 1rem;
  }
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
  height: 60vh;
  position: relative;
  overflow: hidden;
}

.sidebar {
  background-color: #fff;
}

.sidebar.modal-active {
  height: 90vh;
  overflow: hidden;
}

.is-embed {
  .searchbar {
    padding: 10px 0 0;
  }
  .map-column {
    top: 53px;
  }
  .divider-column {
    top: 47px;
  }
}


@media screen and (min-width: 768px){
  .map-container {
    height: 80vh;
    position: sticky;
    top: 0;
    transition: height 0.8s;
  }

  .is-embed {
    .map-container {
      margin-top: 1rem;
      height: calc(100vh - 2em - 2px);
    }
    .sidebar {
      height: calc(100vh - 2em - 2px);
      overflow: scroll;
    }
  }
}

.map-full-height {
  height: 100vh;
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

.divider-column {
  background-color: #fff;
  border-bottom: 2px solid #eee;
  padding: 0.25rem 0;
  z-index: 2025;
  position: -webkit-sticky;
  position: sticky;
  top: 37px;
  padding: 6px 0 6px;
  margin-top: 4px;
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

.clearable-input {
  position: relative;
  flex: 1 1 auto;
  width: 1%;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  margin-bottom: 0;
}
.clearer {
  position: absolute;
  right: 10px;
  top: 30%;
  color: #999;
  cursor: pointer;
}

</style>
