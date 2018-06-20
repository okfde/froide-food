<template>
  <transition name="mapoverlay">
    <div class="food-mapoverlay container-fluid" :class="{'closing': closing}" @touchstart="touchstart" @touchmove="touchmove" @touchend="touchend" :style="{transform: currentTransform}">
      <div class="row">
        <div class="col-12 info-column">
          <div class="mapoverlay-header">
            <h4 class="venue-name">{{ data.name }}</h4>
            <button type="button" class="close" aria-label="Close" @click="$emit('close')">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <p class="venue-address">{{ data.address }}</p>
          <a :href="data.url" class="provider-logo" target="_blank" rel="noopener"></a>
          <div class="clearfix mt-3">
            <div v-if="hasRequest" class="request-status">
              <p :class="requestColor">
                {{ requestStatus }}
              </p>
              <p v-if="requestComplete">
                <a :href="requestUrl" target="_blank" @click.prevent="setDetail">
                  zu den Berichten&nbsp;&rarr;
                </a>
              </p>
              <p v-else>
                <a :href="requestUrl" target="_blank">
                  zur Anfrage&nbsp;&rarr;
                </a>
              </p>
            </div>
            <p v-if="canRequest">
              <a class="btn btn-primary btn-sm make-request-btn" :href="makeRequestUrl"  target="_blank">
                Hygienekontrolle anfragen&nbsp;&rarr;
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import FoodItemMixin from '../lib/mixin'

export default {
  name: 'food-mapoverlay',
  mixins: [FoodItemMixin],
  props: {
    data: {
      type: Object
    },
    config: {
      type: Object
    }
  },
  data () {
    return {
      touchYStart: null,
      touchYCurrent: null,
      defaultOffset: null,
      closing: false
    }
  },
  computed: {
    currentTransform () {
      return `translateY(${this.offset}px)`
    },
    offset () {
      let offset = this.defaultOffset
      if (this.touchYStart !== null && this.touchYCurrent !== null) {
        offset = this.touchYCurrent - this.touchYStart
        if (offset < 0) {
          offset = -Math.min(100, Math.abs(offset / 5))
        }
      }
      return offset
    }
  },
  methods: {
    close () {
      this.closing = true
      this.defaultOffset = 300
      this.touchYStart = null
      this.touchYCurrent = null
      window.setTimeout(() => { this.$emit('close') }, 300)
    },
    touchstart (e) {
      this.touchYStart = e.touches[0].pageY
    },
    touchmove (e) {
      e.preventDefault()
      this.touchYCurrent = e.touches[0].pageY
      if (this.offset > 100) {
        this.close()
      }
    },
    touchend () {
      if (this.offset > 20) {
        this.close()
      } else {
        this.defaultOffset = 0
      }
      this.touchYStart = null
      this.touchYCurrent = null
    }
  }
}
</script>

<style lang="scss" scoped>

.food-mapoverlay {
  position: absolute;
  bottom: 5px;
  left: 3%;
  right: 3%;
  width: 94%;
  z-index: 2400;
  background-color: #fff;
  border-radius: 5px;
}

@media screen and (min-width: 480px){
  .food-mapoverlay {
    left: 15%;
    right: 15%;
    width: 70%;
  }
}

.mapoverlay-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}

.mapoverlay-header .close {
  padding: 0.75rem 1rem;
  margin: -1rem -1rem -1rem auto;
}

.image-column {
  padding: 0 5px;
}

.info-column {
  padding: 8px;
}

.venue-img {
  height: 70px;
  width: 100%;
  object-fit: cover;
}

.venue-name {
  font-size: 1.25rem;
}

.venue-address {
  font-size: 0.8rem;
  margin: 0;
  color: #687683;
  display: inline-block;
  white-space: pre-line;
}

.request-button {
  display: block;
}

.to-request-button {
  display: block;
  color: #28a745;
}

.food-mapoverlay {
  transition: transform 0.1s linear;
}
.food-mapoverlay.closing {
  transition: transform 0.4s linear;
}

.mapoverlay-enter, .mapoverlay-leave-to {
  transform: translateY(300px);
}

.mapoverlay-enter-active, .fade-leave-active {
  transition: transform 0.3s ease-in-out;
}

.mapoverlay-leave-active {
  transition: all .3s ease-in-out;
}


.provider-logo {
  background-image: url('/static/food/images/yelp_logo.png');
  background-repeat: no-repeat;
  background-size: contain;
  display: inline-block;
  float: right;
  width: 65px;
  height: 40px;
  margin: 0.25rem;
}


</style>
