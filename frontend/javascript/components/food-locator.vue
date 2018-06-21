<template>
  <div class="modal-mask" @click.self="close">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            Wo wollen Sie suchen?
          </h5>
          <button type="button" class="close" aria-label="Close" @click="close" v-if="locationKnown">
             <span aria-hidden="true">&times;</span>
           </button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <div v-if="error" class="alert alert-danger">
                Es wurde nichts gefunden.
              </div>

              <p v-if="geolocationAvailable">
                Suchen Sie in einem PLZ-Bereich oder in Ihrer Umgebung.
              </p>
              <p v-else>
                Bitte geben Sie eine Postleitzahl ein, um in der Nähe zu suchen.
              </p>
            </div>
          </div>
          <div class="row justify-content-lg-center">
            <div :class="{'col-lg-5': geolocationAvailable, 'col-lg-8': !geolocationAvailable}">
              <div class="input-group" v-if="false">
                <input type="text" pattern="\d*" class="form-control postcode-input" v-model="postcode" placeholder="PLZ" maxlength="5" @keydown.enter.prevent="postcodeLookup">
                <div class="input-group-append">
                  <button class="btn" :class="{'btn-success': validPostcode, 'btn-outline-secondary': !validPostcode}" type="button" @click.prevent="postcodeLookup">
                    Auf geht’s!
                  </button>
                </div>
              </div>
              <div class="input-group">
                <div class="clearable-input">
                  <input type="text" class="form-control" v-model="location" placeholder="Ort oder PLZ" @keydown.enter.prevent="locationLookup" autofocus>
                  <span class="clearer fa fa-close" v-if="location.length > 0" @click.stop="location = ''"></span>
                </div>
                <div class="input-group-append">
                  <button class="btn" :class="{'btn-success': validLocation, 'btn-outline-secondary': !validLocation}" type="button" @click.prevent="locationLookup" :disabled="!validLocation">
                    Auf geht’s!
                  </button>
                </div>
              </div>
              <div>
                <small>
                  Beispiel: 
                  <template v-for="city in exampleCities">
                    <a href="#" :key="city" @click.prevent="setLocation(city)" class="example-city">{{ city }}</a>
                  </template>
                </small>
              </div>
            </div>
            <template v-if="geolocationAvailable">
              <div class="col-lg-2 or-column">
                <strong>oder</strong>
              </div>
              <div class="col-lg-5">
                <button class="btn btn-primary btn-block" @click.prevent="requestGeolocation" :disabled="determiningGeolocation">
                  <template v-if="geolocationDetermined">
                    <i class="fa fa-dot-circle-o" aria-hidden="true"></i>
                    Zu Ihrem Standort
                  </template>
                  <template v-else-if="determiningGeolocation">
                    <food-loader></food-loader>
                    Ihr Standort wird ermittelt...
                  </template>
                  <template v-else>
                    <i class="fa fa-location-arrow" aria-hidden="true"></i>
                    Ihren Standort ermitteln
                  </template>
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import FoodLoader from './food-loader'

export default {
  name: 'food-locator',
  components: {FoodLoader},
  props: {
    'defaultPostcode': {
      type: String,
      default: ''
    },
    'defaultLocation': {
      type: String,
      default: ''
    },
    'exampleCity': {
      type: String,
      default: ''
    },
    'locationKnown': {
      type: Boolean,
      default: false
    },
    'error': {
      type: Boolean,
      default: false
    }
  },
  data () {
    if (window.navigator && window.navigator.permissions) {
      navigator.permissions.query({'name': 'geolocation'})
        .then((permission) => {
          if (permission.state === 'denied') {
            this.geolocationAllowed = false
          } else if (permission.state === 'granted') {
            this.autoGeolocation = true
            this.requestGeolocation()
          }
        })
    }
    return {
      postcode: this.defaultPostcode,
      location: this.defaultLocation,
      geolocationAllowed: true,
      determiningGeolocation: false,
      geolocationDetermined: false,
      autoGeolocation: false,
      geolocationErrorMessage: null
    }
  },
  computed: {
    validPostcode () {
      return !!this.postcode.match(/^\d{5}$/)
    },
    validLocation () {
      return this.location.length > 0
    },
    geolocationAvailable () {
      return !!window.navigator.geolocation && this.geolocationAllowed
    },
    exampleCities () {
      let examples = ['Berlin', 'Hamburg', 'München']
      if (this.exampleCity === '') {
        return examples
      }
      examples = examples.filter((c) => c !== this.exampleCity)
      return [exampleCity].concat(examples)
    }
  },
  methods: {
    postcodeLookup () {
      this.$emit('postcodeChosen', '' + this.postcode)
      this.$emit('close')
    },
    locationLookup () {
      if (this.validLocation) {
        this.$emit('locationChosen', '' + this.location)
        this.$emit('close')
      }
    },
    setLocation (city) {
      this.location = city
      this.locationLookup()
    },
    requestGeolocation () {
      if (this.geolocationDetermined) {
        this.$emit('close')
        return
      }
      this.determiningGeolocation = true
      navigator.geolocation.getCurrentPosition(
        this.geolocationSuccess,
        this.geolocationError
      )
    },
    close () {
      if (this.locationKnown) {
        this.$emit('close')
      }
    },
    geolocationSuccess (pos) {
      this.determiningGeolocation = false
      this.geolocationDetermined = true
      var crd = pos.coords
      this.$emit('coordinatesChosen', [crd.latitude, crd.longitude])
      if (!this.autoGeolocation) {
        this.$emit('close')
      }
    },
    geolocationError (err) {
      this.determiningGeolocation = false
      if (err) {
        this.geolocationAllowed = false
        this.geolocationErrorMessage = err.message
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  #food-locator {
    z-index: 3000;
  }

  .postcode-input {
    width: 120px;
  }

  .or-column {
    text-align: center;
    padding: 0.5rem;
  }

  .modal-mask {
    position: absolute;
    z-index: 9998;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, .5);
    display: flex;
    transition: opacity .3s ease;
  }
  .is-embed .modal-mask {
    top: 10px;
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

  .example-city {
    text-decoration: underline;
  }

  .example-city:not(:last-child) {
    margin-right: 0.5rem;
  }


</style>
