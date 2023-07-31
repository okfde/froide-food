<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Wo wollen Sie suchen?</h5>
          <button
            type="button"
            class="btn-close"
            aria-label="Close"
            data-bs-dismiss="modal"
            @click="close"
            v-if="locationKnown" />
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <div v-if="error" class="alert alert-danger">
                <span v-if="errorMessage">
                  {{ errorMessage }}
                </span>
                <span v-else> Es wurde nichts gefunden. </span>
              </div>

              <p v-if="geolocationAvailable">
                Suchen Sie nach einem Ort, mit PLZ oder in Ihrer Umgebung.
              </p>
              <p v-else>Bitte geben Sie eine Postleitzahl oder Ort ein.</p>
            </div>
          </div>
          <div class="row justify-content-lg-center">
            <div
              :class="{
                'col-lg-6 col-md-7': geolocationAvailable,
                'col-lg-12': !geolocationAvailable
              }">
              <div class="input-group">
                <div class="clearable-input">
                  <input
                    type="text"
                    class="form-control"
                    v-model="location"
                    placeholder="Ort oder PLZ"
                    @keydown.enter.prevent="locationLookup"
                    ref="locationInput" />
                  <span
                    class="clearer fa fa-close"
                    v-if="location.length > 0"
                    @click.stop="location = ''"></span>
                </div>
                <button
                  class="btn"
                  :class="{
                    'btn-success': validLocation,
                    'btn-outline-secondary': !validLocation
                  }"
                  type="button"
                  @click.prevent="locationLookup"
                  :disabled="!validLocation">
                  Auf geht’s!
                </button>
              </div>
              <div>
                <small>
                  Beispiel:
                  <template v-for="city in exampleCities" :key="city">
                    <a
                      href="#"
                      @click.prevent="setLocation(city)"
                      class="example-city"
                      >{{ city }}</a
                    >
                  </template>
                </small>
              </div>
            </div>
            <template v-if="geolocationAvailable">
              <div class="col-lg-1 col-md-1 or-column">
                <strong>oder</strong>
              </div>
              <div class="col-md-4 col-lg-5">
                <div class="d-grid">
                  <button
                    class="btn btn-primary"
                    @click.prevent="requestGeolocation"
                    :disabled="determiningGeolocation">
                    <template v-if="geolocationDetermined">
                      <i class="fa fa-dot-circle-o" aria-hidden="true"></i>
                      Zu Ihrem Standort
                    </template>
                    <template v-else-if="determiningGeolocation">
                      <span
                        class="spinner-grow spinner-grow-sm"
                        role="status"
                        aria-hidden="true"></span>
                      Ihr Standort wird ermittelt...
                    </template>
                    <template v-else>
                      <i class="fa fa-location-arrow" aria-hidden="true"></i>
                      Ihren Standort ermitteln
                    </template>
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FoodLocator',
  props: {
    defaultPostcode: {
      type: String,
      default: ''
    },
    defaultLocation: {
      type: String,
      default: ''
    },
    exampleCity: {
      type: String,
      default: ''
    },
    locationKnown: {
      type: Boolean,
      default: false
    },
    error: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: ''
    },
    isMobile: {
      type: Boolean,
      default: false
    },
    geolocationDisabled: {
      type: Boolean,
      default: false
    }
  },
  mounted() {
    if (this.$refs.locationInput) {
      this.$refs.locationInput.focus()
    }
  },
  data() {
    if (window.navigator && window.navigator.permissions) {
      navigator.permissions
        .query({ name: 'geolocation' })
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
    validPostcode() {
      return !!this.postcode.match(/^\d{5}$/)
    },
    validLocation() {
      return this.location.length > 0
    },
    geolocationAvailable() {
      return (
        !!window.navigator.geolocation &&
        this.geolocationAllowed &&
        !this.geolocationDisabled
      )
    },
    exampleCities() {
      let examples = ['Berlin', 'Hamburg', 'Köln', 'München']
      if (this.exampleCity === '') {
        return examples
      }
      examples = examples.filter((c) => c !== this.exampleCity)
      return [this.exampleCity].concat(examples)
    }
  },
  methods: {
    postcodeLookup() {
      this.$emit('postcodeChosen', '' + this.postcode)
      this.$emit('close')
    },
    locationLookup() {
      if (this.validLocation) {
        this.$emit('locationChosen', '' + this.location)
        this.$emit('close')
      }
    },
    setLocation(city) {
      this.location = city
      this.locationLookup()
    },
    requestGeolocation() {
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
    close() {
      if (this.locationKnown) {
        this.$emit('close')
      }
    },
    geolocationSuccess(pos) {
      this.determiningGeolocation = false
      this.geolocationDetermined = true
      var crd = pos.coords
      this.$emit('coordinatesChosen', [crd.latitude, crd.longitude])
      if (!this.autoGeolocation) {
        this.$emit('close')
      }
    },
    geolocationError(err) {
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
.postcode-input {
  width: 120px;
}

.or-column {
  text-align: center;
  padding: 0.5rem;
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

.example-city {
  text-decoration: underline;
}

.example-city:not(:last-child) {
  margin-right: 0.5rem;
}
</style>
