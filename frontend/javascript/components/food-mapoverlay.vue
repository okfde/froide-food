<template>
  <div
    class="food-mapoverlay container-fluid"
    :class="{ closing: closing }"
    @touchstart="touchstart"
    @touchmove="touchmove"
    @touchend="touchend"
    :style="{ transform: currentTransform }"
  >
    <div class="row">
      <div class="col-12 info-column">
        <div class="mapoverlay-header">
          <h4 class="venue-name">
            {{ data.name }}
          </h4>
          <button
            type="button"
            class="btn-close"
            aria-label="Close"
            @click="$emit('close')"
          />
        </div>
        <div class="row">
          <div class="col-12">
            <p class="venue-address">{{ data.address }}</p>
            <div class="clearfix mt-3">
              <div v-if="hasRequest" class="request-status">
                <p :class="requestColor">
                  {{ requestStatus }}
                </p>
                <p>
                  <a v-if="requestUrl" :href="requestUrl" target="_blank">
                    zur Anfrage&nbsp;&rarr;
                  </a>
                  <span v-else>Anfrage gestellt!</span>
                </p>
                <p v-if="requestComplete">
                  <a
                    :href="requestUrl"
                    target="_blank"
                    @click.prevent="setDetail"
                  >
                    zu den Berichten&nbsp;&rarr;
                  </a>
                </p>
              </div>
              <p v-if="canRequest">
                <a
                  @click.prevent.stop="startRequest"
                  class="btn btn-primary btn-sm"
                  :href="makeRequestUrl"
                  target="_blank"
                >
                  Hygienekontrolle anfragen&nbsp;&rarr;
                </a>
              </p>
              <FoodFollow
                v-if="user && !requestComplete"
                :follow="data.follow"
                @followed="$emit('followed', $event)"
                @unfollowed="$emit('unfollowed')"
              ></FoodFollow>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FoodItemMixin from '../lib/mixin'
import FoodFollow from './food-follow.vue'

export default {
  name: 'FoodMapoverlay',
  mixins: [FoodItemMixin],
  components: {
    FoodFollow
  },
  props: {
    data: {
      type: Object
    },
    user: {
      type: Object,
      default: null
    },
    config: {
      type: Object
    }
  },
  data() {
    return {
      touchYStart: null,
      touchYCurrent: null,
      defaultOffset: null,
      closing: false
    }
  },
  computed: {
    currentTransform() {
      return `translateY(${this.offset}px)`
    },
    offset() {
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
    close() {
      this.closing = true
      this.defaultOffset = 300
      this.touchYStart = null
      this.touchYCurrent = null
      window.setTimeout(() => {
        this.$emit('close')
      }, 300)
    },
    touchstart(e) {
      this.touchYStart = e.touches[0].pageY
    },
    touchmove(e) {
      e.preventDefault()
      this.touchYCurrent = e.touches[0].pageY
      if (this.offset > 100) {
        this.close()
      }
    },
    touchend() {
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
  z-index: 1001; // over leafleft-bottom
  background-color: var(--bs-body-bg);
  border-radius: 5px;
}

@media screen and (min-width: 480px) {
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
  padding: calc(var(--bs-gutter-x) * 0.5);
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

.provider-credit {
  display: block;
  padding: calc(var(--bs-gutter-x) * 0.5);
  background-color: #f5f5f5;
  margin-right: 5px;
  margin-bottom: 5px;
}

.provider-logo {
  background-repeat: no-repeat;
  background-size: contain;
  height: 40px;
  margin: 0.25rem;
}

.review-count {
  font-size: 0.7rem;
  display: block;
  margin: 0.25rem 0 0;
  padding: 0 0 0.25rem;
  color: #888;
  text-decoration: none;
}
</style>
