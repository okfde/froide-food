<template>
  <div :class="{'food-map-embed': config.embed, 'modal-active': modalActive}" v-scroll="handleSidebarScroll">
    <div class="food-map-container container-fluid" ref="foodMapContainer" id="food-map-container" :class="{'is-embed': config.embed}">

      <div class="searchbar d-block d-md-none" id="searchbar">
        <div class="searchbar-inner">
          <div class="input-group">
            <div class="clearable-input">
              <input type="text" v-model="query" class="form-control" placeholder="Restaurant, Fleischer, etc." @keydown.enter.prevent="userSearch">
              <span class="clearer fa fa-close" v-if="query.length > 0" @click.stop="query = ''"></span>
            </div>
            <div class="input-group-append">
              <button class="btn btn-outline-secondary" type="button" @click="userSearch">
                <i class="fa fa-search" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Suchen</span>
              </button>
            </div>
            <div class="input-group-append mr-auto">
              <button class="btn btn-outline-secondary" @click="showLocator = true">
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
                  <input type="text" v-model="query" class="form-control" placeholder="Restaurant"  @keydown.enter.prevent="userSearch">
                  <span class="clearer fa fa-close" v-if="query.length > 0" @click.stop="query = ''"></span>
                </div>
                <div class="input-group-append">
                  <button class="btn btn-outline-secondary" type="button" @click="userSearch">
                    <i class="fa fa-search" aria-hidden="true"></i>
                    <span class="d-none d-sm-none d-lg-inline">Suchen</span>
                  </button>
                </div>
                <div class="input-group-append">
                  <button class="btn btn-outline-secondary" @click="showLocator = true">
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

              <l-marker v-for="marker in facilities" :key="marker.id"
                  :lat-lng="marker.position" :title="marker.name"
                  :draggable="false" :icon="marker.icon" :options="markerOptions"
                  @click="markerClick(marker, false)"
                  @touchstart.prevent="markerClick(marker, false)" v-focusmarker>
                <l-tooltip :content="marker.name" v-if="!isMobile"/>
                <l-popup :options="popupOptions" v-if="!isMobile">
                  <food-popup :data="marker" :config="config" @detail="setDetail"/>
                </l-popup>
              </l-marker>

            </l-map>
            <food-mapoverlay :data="selectedFacility" :config="config" v-if="stacked && selectedFacility"
              @close="clearSelected"
              @detail="setDetail"></food-mapoverlay>
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
            <food-sidebar-item v-if="searching" v-for="data in fakeFacilities"
              :key="data.id"
              :data="data">
            </food-sidebar-item>
            <food-sidebar-item v-for="data in facilities"
                :key="data.ident" :data="data"
                :config="config"
                :selectedFacilityId="selectedFacilityId"
                @select="markerClick(data, true)"
                @detail="setDetail"
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
        @close="showLocator = false"
        @postcodeChosen="postcodeChosen"
        @coordinatesChosen="coordinatesChosen"
        @locationChosen="locationChosen"
        ></food-locator>
      <food-detail v-if="showDetail" :data="showDetail" @close="showDetail = null" @detailfetched="detailFetched"></food-detail>
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
  components: {
    LMap, LTileLayer, LControlLayers, LControlZoom, LMarker, LPopup, LTooltip,
    FoodPopup, FoodSidebarItem, FoodLocator, FoodMapoverlay, FoodLoader, FoodDetail,
    FoodFilter, SlideUpDown
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
    let city = this.config.city
    if (city.country_code && city.country_code !== 'DE') {
      city = {}
    }

    return {
      zoom: zoom || (city.latitude ? DETAIL_ZOOM_LEVEL : DEFAULT_ZOOM),
      locationKnown: locationKnown,
      showLocator: false,
      showFilter: false,
      showDetail: null,
      filters: this.config.filters,
      maxBounds: L.latLngBounds(GERMANY_BOUNDS),
      city: city.city,
      postcode: '' + (postcode || city.postal_code || ''),
      locationName: '',
      center: center || [
        city.latitude || 51.00289959043832,
        city.longitude || 10.245523452758789
      ],
      selectedFacilityId: null,
      facilityMap: {},
      facilities: [],
      searching: false,
      error: false,
      stacked: this.isStacked(),
      isMapTop: false,
      mapHeight: null,
      isTouch: L.Browser.touch && L.Browser.mobile,
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
    })
    this.map.on('popupclose', (e) => {
      this.clearSelected()
    })
    window.addEventListener('resize', () => {
      this.isStacked()
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
    isMobile () {
      return this.stacked || L.Browser.mobile
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
        scrollWheelZoom: !this.isMobile,
        doubleClickZoom: true,
        zoomControl: false
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
    fakeFacilities () {
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
    preventMapMoved () {
      window.requestAnimationFrame(() => {
        this.mapMoved = false
      })
      this.map.on('viewreset', this.preventMapMovedCallback)
    },
    preventMapMovedCallback () {
      window.requestAnimationFrame(() => {
        this.mapMoved = false
      })
      this.map.off('viewreset', this.preventMapMovedCallback)
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
    search (options = {}) {
      this.mapMoved = false
      this.error = false
      this.searching = true
      this.clearSelected()
      this.facilities = []
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
        radius = Math.round(Math.min(radius, 40000))
        locationParam = `lat=${coordinates.lat}&lng=${coordinates.lng}&radius=${radius}`
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
          this.facilityMap = {}
          this.facilities = data.results.map((r, i) => {
            let d = {
              position: [r.lat, r.lng],
              id: r.ident.replace(/:/g, '-'),
              full: false,
              ...r
            }
            d.icon = this.getIcon(d)
            this.facilityMap[d.id] = i
            return d
          })
          if (options.location) {
            let facilityLocations = this.facilities.map((r) => {
              return L.latLng(r.position[0], r.position[1])
            })
            let bounds = L.latLngBounds(facilityLocations)
            this.map.fitBounds(bounds)
          }
          this.preventMapMoved()
          this.searching = false
        })
    },
    getIcon (r) {
      let iconUrl = r.requests.length > 0 ? this.iconRequested : this.iconUnRequested
      if (this.selectedFacilityId === r.id) {
        iconUrl = r.requests.length > 0 ? this.iconSelectedRequested : this.iconSelectedUnRequested
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
        this.map.closePopup()
        Vue.set(marker, 'icon', this.getIcon(marker))
      }
    },
    markerClick (marker, pan) {
      this.clearSelected()
      if (pan) {
        this.map.panTo(marker.position)
      }
      this.selectedFacilityId = marker.id
      if (!this.stacked) {
        let sidebarId = 'sidebar-' + marker.id
        let sidebarItem = document.getElementById(sidebarId)
        if (sidebarItem && sidebarItem.scrollIntoView) {
          sidebarItem.scrollIntoView({behavior: 'smooth'})
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
      smoothScroll({x: 0, y: y + y2 + 2, el: this.scrollContainer}, 300)
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
        this.map.invalidateSize()
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
      let zoom = this.map.getZoom()
      if (!window.localStorage) {
        return
      }
      window.localStorage.setItem('froide-food:zoom', zoom)
      window.localStorage.setItem('froide-food:center', JSON.stringify(latlng))
    },
    setDetail (data) {
      this.showDetail = data
    },
    detailFetched (data) {
      this.facilities = this.facilities.map((f) => {
        if (f.ident === data.ident) {
          f.requests = data.requests
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
