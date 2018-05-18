<template>
  <transition name="mapoverlay">
    <div class="food-mapoverlay container-fluid" :class="{'closing': closing}" @touchstart="touchstart" @touchmove="touchmove" @touchend="touchend" :style="{transform: currentTransform}">
      <div class="row">
        <!-- <div class="col-3 image-column">
          <a :href="data.url" class="image-column-inner" target="_blank" rel="noopener">
            <img v-if="data.image" :src="data.image" alt="Yelp venue image" class="venue-img img-fluid"/>
            <div v-else class="dummy-image"></div>
            <div :href="data.url" class="provider-logo" target="_blank" rel="noopener"></div>
          </a>
        </div> -->
        <div class="col-12 info-column">
          <div class="mapoverlay-header">
            <h4 class="venue-name">{{ data.name }}</h4>
            <button type="button" class="close" aria-label="Close" @click="$emit('close')">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <p class="venue-address">{{ data.address }}</p>
          <a v-if="!data.request_status" class="request-button" :href="requestUrl"  target="_blank">
            Hygienekontrolle anfragen &rarr;
          </a>
          <a  v-else class="to-request-button" :href="data.request_url" target="_blank">
            zur Anfrage  &rarr;
          </a>
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

</style>