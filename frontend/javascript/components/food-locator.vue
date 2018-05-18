<template>
  <div class="modal-mask">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            Frage nach dem Hygienekontroll&shy;bericht deines Lieblings&shy;restaurants
          </h5>
          <button type="button" class="close" aria-label="Close" @click="$emit('close')">
             <span aria-hidden="true">&times;</span>
           </button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <p v-if="geolocationAvailable">
                Suche in einem PLZ-Bereich oder in deiner Umgebung.
              </p>
              <p v-else>
                Bitte gib eine Postleitzahl ein, um in der Nähe zu suchen.
              </p>
            </div>
          </div>
          <div class="row justify-content-lg-center">
            <div :class="{'col-lg-5': geolocationAvailable, 'col-lg-8': !geolocationAvailable}">
              <div class="input-group">
                <input type="text" pattern="\d*" class="form-control postcode-input" v-model="postcode" placeholder="PLZ" maxlength="5" @keydown.enter.prevent="postcodeLookup">
                <div class="input-group-append">
                  <button class="btn" :class="{'btn-success': validPostcode, 'btn-outline-secondary': !validPostcode}" type="button" @click.prevent="postcodeLookup">
                    Auf geht's!
                  </button>
                </div>
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
    geolocationAvailable () {
      return !!window.navigator.geolocation && this.geolocationAllowed
    }
  },
  methods: {
    postcodeLookup () {
      this.$emit('postcodeChosen', '' + this.postcode)
      this.$emit('close')
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
    geolocationSuccess (pos) {
      this.determiningGeolocation = false
      this.geolocationDetermined = true
      var crd = pos.coords
      this.$emit('locationChosen', [crd.latitude, crd.longitude])
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

<style lang="scss">
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
    position: fixed;
    z-index: 9998;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, .5);
    display: table;
    transition: opacity .3s ease;
  }

</style>