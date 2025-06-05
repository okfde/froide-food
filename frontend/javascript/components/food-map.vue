<template>
  <div>
    <FoodRequest
      v-if="showRequestForm"
      :config="requestConfig"
      :request-form="requestForm"
      :user-info="user"
      :user-form="userForm"
      :data="showRequestForm"
      :current-url="currentUrl"
      @detailfetched="detailFetched"
      @requestmade="requestMade"
      @userupdated="userUpdated"
      @tokenupdated="tokenUpdated"
      @close="requestFormClosed"
    >
    </FoodRequest>
    <div
      v-show="!showRequestForm"
      :class="{ 'food-map-embed': config.embed, 'modal-active': modalActive }"
      v-scroll="handleSidebarScroll"
    >
      <div
        class="food-map-container container-fluid"
        ref="foodMapContainer"
        id="food-map-container"
        :class="{ 'is-embed': config.embed }"
      >
        <div class="searchbar d-block d-md-none" id="searchbar">
          <div class="searchbar-inner">
            <div class="input-group">
              <div class="clearable-input">
                <input
                  type="text"
                  v-model="query"
                  :class="{ 'search-query-active': !!lastQuery }"
                  class="form-control"
                  placeholder="Restaurant, Supermarkt, Kiosk etc."
                  @keydown.enter.prevent="userSearch"
                />
                <span
                  class="clearer fa fa-close"
                  v-if="query.length > 0"
                  @click="clearSearch"
                ></span>
              </div>
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="userSearch"
              >
                <i class="fa fa-search" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Suchen</span>
              </button>
              <button
                class="btn btn-outline-secondary"
                @click="setLocator(true)"
              >
                <i class="fa fa-location-arrow" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Ort</span>
              </button>
              <button
                class="btn btn-outline-secondary"
                :class="{ active: showFilter }"
                @click="openFilter"
              >
                <i class="fa fa-gears" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Filter</span>
              </button>
            </div>
            <SlideUpDown v-model="showFilter" :duration="300">
              <div class="switch-filter">
                <SwitchButton v-model="onlyRequested" color="#FFC006"
                  >nur angefragte Betriebe zeigen</SwitchButton
                >
              </div>
              <FoodFilter
                v-if="false"
                :filters="filters"
                @change="filterChanged"
                @apply="applyFilter"
              ></FoodFilter>
            </SlideUpDown>
          </div>
        </div>
        <div class="row">
          <div class="col-md-8 col-lg-9 order-md-2 map-column">
            <div
              class="map-container"
              ref="foodMap"
              id="food-map"
              :class="mapContainerClass"
              :style="mapContainerStyle"
            >
              <div v-if="showRefresh || searching" class="redo-search">
                <button
                  v-if="showRefresh"
                  class="btn btn-dark"
                  @click="searchArea"
                >
                  Im aktuellen Bereich suchen
                </button>
                <button
                  v-if="searching"
                  class="btn btn-secondary btn-sm disabled"
                >
                  <FoodLoader></FoodLoader>
                  Suche läuft&hellip;
                </button>
              </div>

              <div
                class="map-search d-none d-md-block"
                :class="{ 'map-search-full': !(showRefresh || searching) }"
              >
                <div class="input-group">
                  <div class="clearable-input">
                    <input
                      type="text"
                      v-model="query"
                      :class="{ 'search-query-active': !!lastQuery }"
                      class="form-control"
                      placeholder="Suche nach Restaurant, Kiosk etc."
                      @keydown.enter.prevent="userSearch"
                    />
                    <span
                      class="clearer fa fa-close"
                      v-if="query.length > 0"
                      @click="clearSearch"
                    ></span>
                  </div>
                  <button
                    class="btn btn-outline-secondary"
                    type="button"
                    @click="userSearch"
                  >
                    <i class="fa fa-search" aria-hidden="true"></i>
                    <span class="d-none d-sm-none d-lg-inline">Suchen</span>
                  </button>
                  <button
                    class="btn btn-outline-secondary"
                    @click="setLocator(true)"
                  >
                    <i class="fa fa-location-arrow" aria-hidden="true"></i>
                    <span class="d-none d-lg-inline">Ort</span>
                  </button>
                  <button
                    class="btn btn-outline-secondary"
                    :class="{ active: showFilter }"
                    @click="openFilter"
                  >
                    <i class="fa fa-gears" aria-hidden="true"></i>
                    <span class="d-none d-sm-none d-md-inline">Filter</span>
                  </button>
                </div>
                <SlideUpDown v-model="showFilter" :duration="300">
                  <div class="switch-filter">
                    <SwitchButton v-model="onlyRequested" color="#FFC006"
                      >nur angefragte Betriebe zeigen</SwitchButton
                    >
                  </div>
                </SlideUpDown>
              </div>

              <LMap
                ref="map"
                v-model:zoom="zoom"
                :center="center"
                :options="mapOptions"
                :max-bounds="maxBounds"
                @ready="mapReady"
              >
                <LTileLayer
                  :url="tileUrl"
                  :attribution="tileProvider.attribution"
                />
                <LControlZoom position="bottomright" />
                <LControl position="bottomleft">
                  <ul class="color-legend shadow">
                    <li :style="colorLegend.normal">
                      <span>Jetzt anfragen!</span>
                    </li>
                    <li :style="colorLegend.pending">
                      <span>Anfrage läuft</span>
                    </li>
                    <li :style="colorLegend.success">
                      <span>Anfrage erfolgreich</span>
                    </li>
                    <li :style="colorLegend.failure">
                      <span>Anfrage abgelehnt</span>
                    </li>
                  </ul>
                </LControl>
                <LMarker
                  v-for="marker in venues"
                  :key="marker.id"
                  :lat-lng="marker.position"
                  :title="marker.name"
                  :draggable="false"
                  :options="markerOptions"
                  :z-index-offset="marker.id === selectedVenueId ? 300 : 0"
                  @click="markerClick(marker, false)"
                  @touchstart.prevent="markerClick(marker, false)"
                >
                  <LIcon class-name="food-marker-icon">
                    <div
                      :style="{
                        'background-image': `url(${marker.icon.iconUrl}`
                      }"
                    >
                      <span
                        class="fa"
                        :class="marker.icon.className"
                        :style="{ color: marker.icon.contrastColor }"
                      ></span>
                    </div>
                  </LIcon>
                  <LTooltip
                    :content="marker.escapedName"
                    :options="tooltipOptions"
                    v-if="!isMobile"
                  />
                  <LPopup :options="popupOptions" v-if="!isMobile">
                    <FoodPopup
                      :data="marker"
                      :config="config"
                      @start-request="startRequest"
                      @detail="setDetail"
                    />
                  </LPopup>
                </LMarker>
              </LMap>
              <transition name="mapoverlay">
                <FoodMapoverlay
                  v-if="stacked && selectedVenue"
                  :data="selectedVenue"
                  :config="config"
                  :user="user"
                  @close="clearSelected"
                  @start-request="startRequest"
                  @detail="setDetail"
                  @followed="followedRequest(selectedVenue, $event)"
                  @unfollowed="selectedVenue.follow.follows = false"
                ></FoodMapoverlay>
              </transition>
            </div>
          </div>

          <div class="col-12 d-block d-md-none divider-column" id="divider">
            <p v-if="listShown" class="divider-button">
              <button
                class="btn btn-sm btn-outline-secondary"
                @click.prevent="goToMap"
                @touchend.prevent="goToMap"
              >
                zurück zur Karte
              </button>
            </p>
            <p v-else class="divider-button">
              <button
                class="btn btn-sm btn-outline-secondary"
                @click.prevent="goToList"
                @touchend.prevent="goToList"
              >
                zur Liste
              </button>
            </p>
          </div>

          <div class="col-md-4 col-lg-3 order-md-1 sidebar-column">
            <div
              class="sidebar"
              :class="{ 'modal-active': modalActive }"
              ref="foodList"
              id="food-list"
              v-scroll.window="handleSidebarScroll"
            >
              <div class="new-venue-area" v-if="hasSearched || error">
                <template v-if="searchEmpty">
                  <p v-if="lastQuery">
                    Keine Betriebe mit dem Suchwort „{{ lastQuery }}“ gefunden.
                  </p>
                  <p v-else>Keine Betriebe an diesem Ort gefunden.</p>
                </template>
                <button
                  class="btn btn-sm btn-link mb-1"
                  @click="setNewVenue(true)"
                >
                  Betrieb nicht gefunden?
                </button>
                <a
                  class="btn btn-sm btn-link ms-1 mb-1"
                  target="_blank"
                  href="/kampagnen/lebensmittelkontrolle/faq/#falsch"
                >
                  Daten falsch?
                </a>
              </div>
              <template v-if="searching">
                <FoodSidebarItem
                  v-for="data in fakeVenues"
                  :key="data.id"
                  :data="data"
                >
                </FoodSidebarItem>
              </template>
              <FoodSidebarItem
                v-for="data in venues"
                :key="data.id"
                :data="data"
                :config="config"
                :user="user"
                :selected-venue-id="selectedVenueId"
                @select="markerClick(data, true)"
                @detail="setDetail"
                @start-request="startRequest"
                @image-loaded="imageLoaded"
                @followed="followedRequest(data, $event)"
                @unfollowed="data.follow.follows = false"
              ></FoodSidebarItem>
            </div>
          </div>
        </div>
        <FoodLocator
          :default-postcode="postcode"
          :default-location="locationName"
          :example-city="city"
          :location-known="locationKnown"
          :error="error"
          :error-message="locatorErrorMessage"
          :geolocation-disabled="geolocationDisabled"
          :is-mobile="isMobile"
          ref="foodlocator"
          @close="setLocator(false)"
          @postcode-chosen="postcodeChosen"
          @coordinates-chosen="coordinatesChosen"
          @location-chosen="locationChosen"
        >
        </FoodLocator>
        <FoodDetail
          :data="showDetail"
          ref="fooddetail"
          @close="setDetail(null)"
          @detailfetched="detailFetched"
        >
        </FoodDetail>
        <FoodNewVenue
          ref="newvenue"
          @close="setNewVenue(false)"
          @detailfetched="detailFetched"
          @venuecreated="venueCreated"
        >
        </FoodNewVenue>
      </div>
    </div>
  </div>
</template>

<script>
import * as L from 'leaflet/dist/leaflet-src.esm'

import 'leaflet/dist/leaflet.css'

import bbox from '@turf/bbox'
import {
  LControl,
  LControlZoom,
  LIcon,
  LMap,
  LMarker,
  LPopup,
  LTileLayer,
  LTooltip
} from '@vue-leaflet/vue-leaflet'
import Modal from 'bootstrap/js/dist/modal'
import SlideUpDown from 'vue3-slide-up-down'
import smoothScroll from '../lib/smoothscroll'

import FoodDetail from './food-detail'
import FoodFilter from './food-filter'
import FoodLoader from './food-loader'
import FoodLocator from './food-locator'
import FoodMapoverlay from './food-mapoverlay'
import FoodNewVenue from './food-new-venue'
import FoodPopup from './food-popup'
import FoodRequest from './food-request'
import FoodSidebarItem from './food-sidebar-item'
import SwitchButton from './switch-button'

import {
  COLORS,
  canUseLocalStorage,
  getContrastColor,
  getPinColor,
  getPinURL,
  getPlaceStatus,
  getQueryVariable,
  latlngToGrid
} from '../lib/utils'

function escapeHTML(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/'/g, '&apos;')
    .replace(/"/g, '&quot;')
}

const getIdFromPopup = (e) => {
  const node = e.popup._content.firstChild
  return node.id.split('-').slice(1).join('-')
}

const scroll = {
  mounted(el, binding) {
    let scrollElement = el
    if (binding.modifiers.window) {
      scrollElement = window
    }
    const f = function (evt) {
      if (binding.value(evt, el)) {
        scrollElement.removeEventListener('scroll', f)
      }
    }
    scrollElement.addEventListener('scroll', f)
  }
}

const GERMANY_BOUNDS = [
  [56.9449741808516, 24.609375000000004],
  [44.402391829093915, -3.5156250000000004]
]
const DETAIL_ZOOM_LEVEL = 12
const DEFAULT_ZOOM = 6
const DEFAULT_POS = [51.00289959043832, 10.245523452758789]
const MIN_DISTANCE_MOVED_REFRESH = 300 // in meters
const MAX_VENUES = 500
const MIN_MAP_HEIGHT = 300

function getColorMode() {
  return document.documentElement.getAttribute('data-bs-theme') || 'light'
}

export default {
  name: 'FoodMap',
  directives: {
    scroll
  },
  props: {
    config: {
      type: Object,
      required: true
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
      type: Object,
      required: true
    },
    requestConfig: {
      type: Object,
      required: true
    }
  },
  components: {
    LMap,
    LTileLayer,
    LIcon,
    LControlZoom,
    LControl,
    LMarker,
    LPopup,
    LTooltip,
    FoodPopup,
    FoodSidebarItem,
    FoodLocator,
    FoodMapoverlay,
    FoodLoader,
    FoodDetail,
    FoodFilter,
    FoodRequest,
    FoodNewVenue,
    SlideUpDown,
    SwitchButton
  },
  data() {
    let locationKnown = false

    let zoom = null
    let center = null
    let postcode = null
    let requestsMade = []

    const latlng = getQueryVariable('latlng')
    const query = getQueryVariable('query')
    const paramIdent = getQueryVariable('ident')

    let city = this.config.city
    if (city.country_code && city.country_code !== 'DE') {
      city = {}
    }

    if (latlng) {
      const parts = latlng.split(',')
      center = [parseFloat(parts[0]), parseFloat(parts[1])]
      if (center[0] && center[1]) {
        zoom = DETAIL_ZOOM_LEVEL
      }
    }

    if (canUseLocalStorage(window)) {
      requestsMade = JSON.parse(
        window.localStorage.getItem('froide-food:requestsmade')
      )
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

    const maxBounds = L.latLngBounds(GERMANY_BOUNDS)
    if (!maxBounds.contains(L.latLng(center))) {
      center = DEFAULT_POS
    }

    if (center[0] !== DEFAULT_POS[0]) {
      locationKnown = true
      zoom = zoom || DETAIL_ZOOM_LEVEL
    } else {
      zoom = DEFAULT_ZOOM
    }

    this.$root.csrfToken = document.querySelector(
      '[name=csrfmiddlewaretoken]'
    ).value

    return {
      zoom: zoom,
      locationKnown: locationKnown,
      showLocator: false,
      locatorModal: null,
      showFilter: false,
      showDetail: null,
      detailModal: null,
      showRequestForm: null,
      autoUpdate: true,
      showNewVenue: false,
      newVenueModal: null,
      user: this.userInfo,
      filters: this.config.filters,
      maxBounds: maxBounds,
      city: city.city,
      postcode: '' + (postcode || city.postal_code || ''),
      locationName: '',
      center: center,
      requestsMade: requestsMade,
      selectedVenueId: null,
      venueMap: {},
      venues: [],
      searching: false,
      hasSearched: false,
      searchCenter: null,
      searchEmpty: false,
      error: false,
      locatorErrorMessage: '',
      geolocationDisabled: false,
      stacked: this.isStacked(),
      isMapTop: false,
      mapHeight: null,
      isTouch: navigator.maxTouchPoints > 0,
      listShown: false,
      query: query || '',
      onlyRequested: false,
      lastQuery: '',
      paramIdent: paramIdent,
      mapMoved: false,
      autoMoved: false,
      autoMovedTimeout: null,
      alreadyRequested: {},
      tooltipOffset: L.point([-10, -50]),
      markerOptions: {
        riseOnHover: true
      },
      colorMode: getColorMode(),
      tileProvider: {
        name: 'Carto',
        // url: 'https://api.mapbox.com/styles/v1/{username}/{style}/tiles/{tileSize}/{z}/{x}/{y}{r}?access_token={accessToken}',
        // url: 'https://api.tiles.mapbox.com/v4/{style}/{z}/{x}/{y}.png?access_token={accessToken}',
        // url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>',
        options: {
          // style: 'mapbox.streets',
          // username: 'okfde',
          // tileSize: 512,
          // r: L.Browser.retina ? '@2x' : '',
          // accessToken: 'pk.eyJ1Ijoib2tmZGUiLCJhIjoiY2p3aHBpZ2wzMjVxbTQ4bWduM2YwenQ2eCJ9.kzkjyGM8xIEShOZ7ekH5AA'
        }
      }
    }
  },
  created() {
    if ('serviceWorker' in navigator && this.config.swUrl) {
      const scope = this.config.swUrl.replace(/^(.*\/)[\w.]+$/, '$1')
      navigator.serviceWorker
        .register(this.config.swUrl, { scope: scope })
        .then(function (reg) {
          console.log('ServiceWorker registration successful!', reg.scope)
        })
        .catch(function (err) {
          console.log('ServiceWorker registration failed: ', err)
        })
    }

    const observer = new MutationObserver(
      () => (this.colorMode = getColorMode())
    )
    observer.observe(document.documentElement, {
      attributeFilter: ['data-bs-theme'],
      attributeOldValue: true
    })
  },
  computed: {
    map() {
      return this.$refs.map.leafletObject
    },
    tileUrl() {
      return `//cartodb-basemaps-{s}.global.ssl.fastly.net/${
        this.colorMode
      }_all/{z}/{x}/{y}${L.Browser.retina ? '@2x' : ''}.png`
    },
    currentUrl() {
      let url = `${this.config.appUrl}?latlng=${this.center[0]},${this.center[1]}`

      if (this.selectedVenueId) {
        url += `&ident=${encodeURIComponent(this.selectedVenue.ident)}`
        url += `&query=${encodeURIComponent(this.selectedVenue.name)}`
      } else if (this.query) {
        url += `&query=${encodeURIComponent(this.query)}`
      }
      return url
    },
    isMobile() {
      return this.stacked || L.Browser.mobile
    },
    iconCategoryMapping() {
      const filterIconMapping = {}
      this.filters.forEach((f) => {
        f.categories.forEach((c) => {
          filterIconMapping[c] = f.icon
        })
      })
      return filterIconMapping
    },
    filterCategories() {
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
    mapOptions() {
      return {
        scrollWheelZoom: !this.isMobile,
        doubleClickZoom: true,
        zoomControl: false,
        maxZoom: 18
      }
    },
    tooltipOptions() {
      return {
        offset: L.point(0, -40),
        direction: 'top'
      }
    },
    dividerSwitchHeight() {
      return window.innerHeight / 2
    },
    selectedVenue() {
      if (this.selectedVenueId) {
        return this.venues[this.venueMap[this.selectedVenueId]]
      }
      return null
    },
    popupOptions() {
      return {
        autoPanPaddingTopLeft: L.point([5, 85]),
        maxWidth: Math.round(window.innerWidth * 0.7)
      }
    },
    showRefresh() {
      return this.mapMoved && this.zoom >= 10
    },
    scrollContainer() {
      return this.config.embed
        ? document.querySelector('.food-map-embed')
        : window
    },
    mapContainerClass() {
      if (this.isMapTop && !this.stacked) {
        return 'map-full-height'
      }
      return ''
    },
    mapContainerStyle() {
      if (this.mapHeight === null) {
        return ''
      }
      return `height: ${this.mapHeight}px`
    },
    fakeVenues() {
      const a = []
      for (let i = 0; i < 50; i += 1) {
        a.push({ id: 'fake-' + i })
      }
      return a
    },
    modalActive() {
      return this.showLocator || this.showDetail || this.showNewVenue
    },
    colorLegend() {
      return {
        normal: `background-image: url('${getPinURL(COLORS.normal)}')`,
        pending: `background-image: url('${getPinURL(COLORS.pending)}')`,
        success: `background-image: url('${getPinURL(COLORS.success)}')`,
        failure: `background-image: url('${getPinURL(COLORS.failure)}')`
      }
    }
  },
  methods: {
    mapReady() {
      this.map.attributionControl.setPrefix('')
      this.map.on('zoomend', () => {
        this.mapHasMoved()
        this.recordMapPosition()
      })
      this.map.on('moveend', () => {
        if (this.searchCenter !== null) {
          const currentPosition = this.map.getCenter()
          const distance = this.searchCenter.distanceTo(currentPosition)
          if (distance < MIN_DISTANCE_MOVED_REFRESH) {
            return
          }
        }
        this.mapHasMoved()
        this.recordMapPosition()
      })
      this.map.on('click', () => {
        this.clearSelected()
      })
      this.map.on('popupopen', (e) => {
        const nodeId = getIdFromPopup(e)
        this.selectedVenueId = nodeId
      })
      this.map.on('popupclose', () => {
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
    coordinatesChosen(latlng) {
      const center = L.latLng(latlng)
      if (!this.maxBounds.contains(center)) {
        this.geolocationDisabled = true
        this.locatorErrorMessage =
          'Dein Ort scheint nicht in Deutschland zu sein!'
        this.setLocator(true)
        return
      }
      this.geolocationDisabled = false
      this.locatorErrorMessage = ''
      this.locationKnown = true
      this.map.setView(center, DETAIL_ZOOM_LEVEL)
      this.search({ coordinates: center })
      this.preventMapMoved()
    },
    locationChosen(location) {
      this.locationName = location
      this.search({ location: location })
    },
    postcodeChosen(postcode) {
      window.localStorage.setItem('froide-food:postcode', postcode)
      window
        .fetch(`/api/v1/georegion/?kind=zipcode&name=${postcode}&limit=1`)
        .then((response) => {
          return response.json()
        })
        .then((data) => {
          if (data['meta']['total_count'] === 0) {
            return
          }
          this.locationKnown = true
          const geoRegion = data.objects[0]
          let bounds = bbox(geoRegion.geom)
          bounds = L.latLngBounds([
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]]
          ])
          const coords = geoRegion.centroid.coordinates
          const center = L.latLng([coords[1], coords[0]])
          this.map.fitBounds([bounds.getSouthWest(), bounds.getNorthEast()])
          this.search({ coordinates: center, bounds })
          this.preventMapMoved()
        })
    },
    filterChanged(filter) {
      this.filters = this.filters.map((f) => {
        if (f.name === filter.name) {
          f.active = !f.active
        }
        return f
      })
    },
    applyFilter() {
      this.showFilter = false
      this.search()
    },
    openFilter() {
      this.showFilter = !this.showFilter
      if (this.isMobile) {
        this.goToMap()
      }
    },
    mapHasMoved() {
      if (this.autoMoved) {
        return
      }
      this.mapMoved = true
      if (this.autoUpdate) {
        this.searchArea()
      }
    },
    preventMapMoved() {
      this.autoMoved = true
      if (this.autoMovedTimeout !== null) {
        window.clearTimeout(this.autoMovedTimeout)
      }
      this.autoMovedTimeout = window.setTimeout(() => {
        this.autoMoved = false
        this.autoMovedTimeout = null
      }, 1500)
    },
    userSearch() {
      if (this.query.match(/^\d{5}$/)) {
        const p = this.query
        this.query = ''
        return this.postcodeChosen(p)
      }
      this.search({ queryStart: true })
    },
    clearSearch() {
      this.query = ''
      this.search()
    },
    searchArea() {
      this.search()
    },
    search(options = {}) {
      this.mapMoved = false
      this.error = false
      if (this.searching) {
        // we are already searching
        return
      }
      this.searchCenter = this.map.getCenter()
      this.searching = true
      this.searchEmpty = false
      this.clearSelected()
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
          this.map.distance(bounds.getNorthEast(), bounds.getNorthWest()),
          this.map.distance(bounds.getNorthEast(), bounds.getSouthEast())
        )
        radius = Math.max(Math.round(Math.min(radius, 40000) / 100) * 100, 500)
        const reqCoords = latlngToGrid(coordinates, radius)
        locationParam = `lat=${reqCoords.lat}&lng=${reqCoords.lng}`
        if (!this.query) {
          locationParam += `&radius=${radius}&zoom=${this.zoom}`
        }
      }
      this.lastQuery = this.query
      const categories = this.filterCategories
      let cats = categories.map((c) => `categories=${encodeURIComponent(c)}`)
      if (cats.length > 0) {
        cats = '&' + cats.join('&')
      } else {
        cats = ''
      }
      let onlyRequested = ''
      if (this.onlyRequested) {
        onlyRequested = '&requested=1'
      }
      window
        .fetch(
          `/api/v1/venue/?q=${encodeURIComponent(
            this.query
          )}${cats}&${locationParam}${onlyRequested}`
        )
        .then((response) => {
          return response.json()
        })
        .then(this.searchDone(options))
    },
    searchDone(options) {
      return (data) => {
        if (data.error) {
          console.warn('Error requesting the API')
          this.goToMap()
          this.location = ''
          this.searching = false
          this.error = true
          this.showLocator = true
          return
        }
        this.hasSearched = true
        if (data.results.length === 0) {
          this.searchEmpty = true
        }
        this.locationKnown = true
        const requestMapping = {}
        let hasRequests = false

        if (this.onlyRequested || this.query) {
          this.venues = []
        } else if (this.venues.length > MAX_VENUES) {
          this.venues = this.venues.slice(0, MAX_VENUES)
        }
        const duplicates = new Set()
        this.venues.forEach((v) => {
          duplicates.add(this.getVenueId(v))
        })
        const newVenues = data.results
          .filter((r) => {
            const vid = this.getVenueId(r)
            // Filter out duplicates
            return !duplicates.has(vid)
          })
          .map((r) => {
            const d = this.createVenue(r)
            if (d.requests.length > 0 && d.requests[0].id !== null) {
              hasRequests = true
              requestMapping[d.requests[0].id] = d.id
            }
            if (this.paramIdent && r.ident.indexOf(this.paramIdent) !== -1) {
              this.selectedVenueId = d.id
            }
            if (this.alreadyRequested[d.id]) {
              d.requested = true
            }
            return d
          })

        const resultCoordinates = newVenues.map((r) => {
          return L.latLng(r.position[0], r.position[1])
        })
        const resultBounds = L.latLngBounds(resultCoordinates)

        this.venues = [...newVenues, ...this.venues]
        this.venueMap = {}
        this.venues.forEach((d, i) => {
          this.venueMap[d.id] = i
        })

        if (options.location && resultCoordinates.length > 0) {
          if (!this.maxBounds.contains(resultBounds)) {
            this.locatorErrorMessage =
              'Dein Ort scheint nicht in Deutschland zu sein!'
            this.setLocator(true)
            return
          }
          this.map.fitBounds([
            resultBounds.getSouthWest(),
            resultBounds.getNorthEast()
          ])
        } else if ((this.query || this.onlyRequested) && options.queryStart) {
          this.map.fitBounds([
            resultBounds.getSouthWest(),
            resultBounds.getNorthEast()
          ])
        }
        this.preventMapMoved()
        this.searching = false
        if (hasRequests && this.userInfo) {
          this.getFollowers(requestMapping)
        }
      }
    },
    getFollowers(requestMapping) {
      const requestIds = []
      for (const key in requestMapping) {
        requestIds.push(key)
      }
      const requests = requestIds.join(',')
      window
        .fetch(`/api/v1/following/?request=${requests}`)
        .then((response) => {
          return response.json()
        })
        .then((data) => {
          data.objects.forEach((obj) => {
            const parts = obj.request.split('/')
            const requestId = parseInt(parts[parts.length - 2])
            const venueId = requestMapping[requestId]
            const venueIndex = this.venueMap[venueId]
            const venue = this.venues[venueIndex]
            if (venue) {
              venue.follow = obj
            }
          })
        })
    },
    getVenueId(venue) {
      return venue.ident.replace(/:/g, '-')
    },
    createVenue(r) {
      const d = {
        position: [r.lat, r.lng],
        id: this.getVenueId(r),
        full: false,
        escapedName: escapeHTML(r.name),
        ...r
      }
      d.icon = this.getIcon(d)
      return d
    },
    getIcon(r) {
      const status = getPlaceStatus(r)
      const selected = this.selectedVenueId === r.id
      const color = getPinColor(status, selected)
      const iconUrl = getPinURL(color)
      return {
        iconUrl: iconUrl,
        className: this.iconCategoryMapping[r.category] || '',
        contrastColor: getContrastColor(status)
      }
    },
    clearSelected() {
      if (this.selectedVenueId === null) {
        return
      }
      const marker = this.venues[this.venueMap[this.selectedVenueId]]
      this.selectedVenueId = null
      if (marker) {
        this.map.closePopup()
        marker.icon = this.getIcon(marker)
      }
    },
    markerClick(marker, pan) {
      this.clearSelected()
      if (pan) {
        this.map.panTo(marker.position)
      }
      this.selectedVenueId = marker.id
      if (!this.stacked) {
        const sidebarId = 'sidebar-' + marker.id
        const sidebarItem = document.getElementById(sidebarId)
        if (sidebarItem) {
          if (sidebarItem.scrollIntoView) {
            const scrollDifference = Math.abs(
              sidebarItem.getBoundingClientRect().top - window.pageYOffset
            )
            sidebarItem.scrollIntoView({
              behavior: scrollDifference < 2000 ? 'smooth' : 'instant',
              block: 'nearest'
            })
          } else {
            window.scrollTo(0, sidebarItem.offsetTop)
          }
        }
      } else {
        this.goToMap()
      }
      marker.icon = this.getIcon(marker)
      this.preventMapMoved()
    },
    imageLoaded(data) {
      data.imageLoaded = true
    },
    goToMap() {
      const fmc = this.$refs.foodMapContainer
      if (Math.abs(fmc.getBoundingClientRect().top) < 100) {
        return
      }
      const y = fmc.offsetTop
      smoothScroll({ x: 0, y: y, el: this.scrollContainer }, 300)
    },
    goToList() {
      const y = this.$refs.foodMapContainer.offsetTop
      const y2 = this.$refs.foodMap.getBoundingClientRect().height
      smoothScroll({ x: 0, y: y + y2 + 5, el: this.scrollContainer }, 300)
    },
    isStacked() {
      this.stacked = window.innerWidth < 768
      return this.stacked
    },
    handleSidebarScroll() {
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
      if (this.$refs.foodList) {
        const listTop = this.$refs.foodList.getBoundingClientRect().top
        if (listTop < this.dividerSwitchHeight) {
          if (!this.listShown) {
            this.showFilter = false
          }
          this.listShown = true
        } else {
          this.listShown = false
        }
      }
      if (this.$refs.foodMap) {
        const mapRect = this.$refs.foodMap.getBoundingClientRect()
        const mapTop = mapRect.top
        const isMapTop = mapTop <= 0
        if (this.map && isMapTop !== this.isMapTop) {
          window.setTimeout(() => {
            this.map.invalidateSize()
            this.preventMapMoved()
          }, 1000)
          this.preventMapMoved()
        }
        this.isMapTop = isMapTop
        if (!this.stacked) {
          if (!isMapTop) {
            this.mapHeight = Math.max(
              window.innerHeight - mapTop,
              MIN_MAP_HEIGHT
            )
          } else {
            this.mapHeight = null
          }
        }
      }
    },
    recordMapPosition() {
      const latlng = this.map.getCenter()
      this.center = [latlng.lat, latlng.lng]
      const zoom = this.map.getZoom()
      if (!canUseLocalStorage(window)) {
        return
      }
      window.localStorage.setItem('froide-food:zoom', zoom)
      window.localStorage.setItem('froide-food:center', JSON.stringify(latlng))
    },
    setDetail(data) {
      if (this.detailModal === null) {
        this.detailModal = new Modal(this.$refs.fooddetail.$el)
        this.$refs.fooddetail.$el.addEventListener('hidden.bs.modal', () => {
          this.setDetail(null)
        })
      }
      this.showDetail = data
      if (data) {
        this.detailModal.show()
      } else {
        this.detailModal.hide()
      }
    },
    setLocator(data) {
      if (this.locatorModal === null) {
        this.locatorModal = new Modal(this.$refs.foodlocator.$el)
        this.$refs.foodlocator.$el.addEventListener('hidden.bs.modal', () => {
          this.setLocator(false)
        })
      }
      this.showLocator = data
      if (data) {
        this.locatorModal.show()
      } else {
        this.locatorModal.hide()
        this.goToMap()
      }
    },
    setNewVenue(show) {
      if (this.newVenueModal === null) {
        this.newVenueModal = new Modal(this.$refs.newvenue.$el)
        this.$refs.newvenue.$el.addEventListener('hidden.bs.modal', () => {
          this.setNewVenue(false)
        })
      }
      this.showNewVenue = show
      if (show) {
        this.newVenueModal.show()
        this.goToMap()
      } else {
        this.newVenueModal.hide()
      }
    },
    startRequest(data) {
      this.markerClick(data, true)
      this.showRequestForm = data
      this.goToMap()
    },
    requestFormClosed() {
      this.showRequestForm = null
      this.goToMap()
    },
    requestMade(data) {
      this.alreadyRequested[data.id] = true
    },
    detailFetched(data) {
      this.venues = this.venues.map((f) => {
        if (f.ident === data.ident) {
          f.requests = data.requests
          f.address = data.address
          f.publicbody = data.publicbody
          f.makeRequestURL = data.makeRequestURL
          f.userRequestCount = data.userRequestCount
          f.icon = this.getIcon(data)
          f.full = true
          f.authority_cooperative = data.authority_cooperative || false
          f.authority_title = data.authority_title || ''
          f.authority_description = data.authority_description || ''
          return f
        }
        return f
      })
    },
    venueCreated(data) {
      const newVenue = this.createVenue(data)
      if (this.venueMap[newVenue.id] === undefined) {
        this.venues.push(newVenue)
        this.venueMap[newVenue.id] = this.venues.length - 1
      } else {
        this.detailFetched(data)
      }
      this.startRequest(newVenue)
    },
    followedRequest(data, resourceUri) {
      data.follow.follows = true
      data.follow.resource_uri = resourceUri
    },
    tokenUpdated(token) {
      this.$root.csrfToken = token
    },
    userUpdated(user) {
      this.user = user
    }
  },
  watch: {
    onlyRequested(newVal) {
      if (newVal) {
        this.search({ queryStart: true })
      }
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
  fill: darken($icon-normal, 30%);
}

.icon-pending {
  fill: $icon-pending;
}

.icon-pending.selected {
  fill: darken($icon-pending, 30%);
}

.icon-success {
  fill: $icon-normal;
}

.icon-success.selected {
  fill: darken($icon-success, 30%);
}

.icon-failure {
  fill: $icon-failure;
}

.icon-failure.selected {
  fill: darken($icon-failure, 30%);
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

@media screen and (min-width: 768px) {
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
  z-index: 910;
  background-color: var(--bs-body-bg);
  margin: 0 calc(var(--bs-gutter-x) * -0.5);
}

.searchbar-inner {
  padding: 0;
}

.map-search {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 910;
  width: 50%;
  transition: width 0.8s ease-out;
  margin-top: 1rem;
  margin-right: 1rem;
  background-color: var(--bs-body-bg);
}

.map-search-full {
  width: 80%;
}

@media screen and (max-width: 960px) {
  .map-search {
    width: 60%;
  }

  .map-search-full {
    width: 90%;
  }
}

.redo-search {
  position: absolute;
  z-index: 920;
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

@media screen and (min-width: 768px) {
  .redo-search {
    left: 0;
    width: 30%;
    text-align: left;
    margin-left: 1rem;

    .btn {
      font-size: 0.85rem;
    }
  }
}

@media screen and (min-width: 768px) {
  .searchbar-inner {
    padding: 0 calc(var(--bs-gutter-x) * 0.5);
  }
}

.map-column {
  position: -webkit-sticky;
  position: sticky;
  top: 38px;

  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px) {
  .map-column {
    padding-right: calc(var(--bs-gutter-x) * 0.5);
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
  background-color: var(--bs-body-bg);
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

@media screen and (min-width: 768px) {
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
  z-index: 900;
  margin-top: -1px;
  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px) {
  .sidebar-column {
    padding-right: 0px;
    padding-left: calc(var(--bs-gutter-x) * 0.5);
  }
}

.divider-column {
  background-color: var(--bs-body-bg);
  border-bottom: 2px solid #eee;
  padding: 0.25rem 0;
  z-index: 900;
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
    background-color: var(--bs-body-bg);
    color: #333;
    border-radius: 5px;
    text-decoration: underline;
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

.clearable-input .form-control {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.clearer {
  position: absolute;
  right: 10px;
  top: 30%;
  color: #999;
  cursor: pointer;
}

.search-query-active {
  background-color: #f7dc8c;
}

.new-venue-area {
  text-align: center;
  padding: calc(var(--bs-gutter-x) * 0.5) 0;
}

.switch-filter {
  display: flex;
  justify-content: flex-end;
  padding: calc(var(--bs-gutter-x) * 0.5);
  background-color: var(--bs-body-bg);
}

.color-legend {
  margin-bottom: 0;
  padding: 0.5rem;
  background-color: var(--bs-body-bg);
  list-style: none;
}

.color-legend li {
  background-repeat: no-repeat;
  padding-left: 1.5rem;
}

.color-legend li span {
  color: var(--bs-body);
}

.food-marker-icon > div {
  background-repeat: no-repeat;
  background-position: center;
  margin-left: -12px;
  margin-top: -41px;
  width: 25px;
  height: 41px;
}
.food-marker-icon > div > span {
  font-size: 11px;
  display: inline-block;
  pointer-events: none;
  text-align: center;
  line-height: 41px;
  width: 25px;
  margin-left: 0;
  margin-top: -3px;
}
</style>

<style global>
.leaflet-popup-content-wrapper,
.leaflet-popup-tip,
.leaflet-bar a {
  background: var(--bs-body-bg);
  color: var(--bs-body);
}

.leaflet-bar a.leaflet-disabled {
  background: var(--bs-body-bg);
}

.leaflet-container {
  background-color: var(--bs-secondary-bg);
}

.leaflet-container .leaflet-control-attribution,
.leaflet-container .leaflet-control-attribution a {
  background: var(--bs-body-bg);
  color: var(--bs-secondary);
}

.leaflet-control-zoom-in,
.leaflet-control-zoom-in:hover,
.leaflet-control-zoom-out,
.leaflet-control-zoom-out:hover {
  text-decoration: none;
}

.mapoverlay-enter-from,
.mapoverlay-leave-to {
  transform: translateY(300px);
}

.mapoverlay-move,
.mapoverlay-enter-active,
.mapoverlay-leave-active {
  transition: transform 0.5s ease-in-out;
}

.mapoverlay-leave-active {
  position: absolute;
}
</style>
