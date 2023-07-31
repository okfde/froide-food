<template>
  <div class="sidebar-item" :id="'sidebar-' + itemId">
    <div
      class="sidebar-item-inner"
      :class="{ requested: hasRequest, highlighted: isSelected }"
      @click="$emit('select', data)">
      <div class="container-fluid">
        <div class="row">
          <div v-if="isDummy" class="col-3 col-md-4 image-column">
            <div class="image-column-inner">
              <div
                class="dummy-provider dummy"
                :class="{ 'dummy-blinker': isDummy }"></div>
            </div>
          </div>
          <div class="col info-column">
            <h5 v-if="data.name" class="venue-name">
              {{ data.name }}
              <small v-if="osmLink" class="float-end">
                <a
                  :href="osmLink"
                  class="text-muted"
                  target="_blank"
                  rel="noopener">
                  <span class="fa fa-map-o text-body"></span>
                  <span class="visually-hidden">OpenStreetMap</span>
                </a>
              </small>
            </h5>
            <div v-else class="venue-name-dummy dummy dummy-blinker"></div>

            <p v-if="data.address" class="venue-address">{{ data.address }}</p>
            <div
              v-else-if="isDummy"
              class="venue-address-dummy dummy dummy-blinker"></div>
            <template v-if="!isDummy">
              <div v-if="hasRequest" class="request-status">
                <p :class="requestColor">
                  {{ requestStatus }}
                </p>
                <p>
                  <a v-if="requestUrl" :href="requestUrl" target="_blank">
                    zur Anfrage&nbsp;&rarr;
                  </a>
                  <span v-else>Anfrage gestellt, Bestätigung läuft...</span>
                </p>
                <p v-if="requestComplete">
                  <a
                    :href="requestUrl"
                    target="_blank"
                    @click.prevent.stop="setDetail">
                    zu den Berichten&nbsp;&rarr;
                  </a>
                </p>
              </div>
              <p v-if="canRequest">
                <a
                  @click.prevent.stop="startRequest"
                  class="btn btn-primary btn-sm"
                  :href="makeRequestUrl"
                  target="_blank">
                  Hygienekontrolle anfragen&nbsp;&rarr;
                </a>
              </p>
              <food-follow
                v-if="user && !requestComplete"
                :follow="data.follow"
                @followed="$emit('followed', $event)"
                @unfollowed="$emit('unfollowed')"></food-follow>
            </template>
            <div v-else class="dummy-actions dummy"></div>
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
  name: 'FoodSidebarItem',
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
    selectedVenueId: {
      type: String
    },
    config: {
      type: Object
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar-item {
  padding: 0;
  width: 100%;
}

.sidebar-item-inner {
  padding: 1rem 0 1rem;
  border-bottom: 2px solid #eee;
}

.sidebar-item:first-child .sidebar-item-inner {
  padding-top: 0.5rem;
}

@media screen and (min-width: 768px) {
  .sidebar-item:first-child .sidebar-item-inner {
    padding-top: 1rem;
  }
}

.sidebar-item:last-child .sidebar-item-inner {
  border-bottom: 0px;
}

.image-column {
  padding: 0 5px 0 5px;
  min-width: 110px;
}

@media screen and (min-width: 768px) {
  .image-column {
    padding: 0 5px 0 5px;
  }
}

@media screen and (min-width: 768px) {
  .map-container {
    height: 80vh;
  }
  .sidebar {
    height: 80vh;
    overflow-y: scroll;
  }
}

.image-column-inner,
.image-column-inner-link {
  display: block;
  background-color: #eee;
  padding: 0;
}

.image-column-inner:hover,
.image-column-inner-link:hover {
  text-decoration: none;
}

.image-column-inner-link {
  cursor: pointer;
}

.info-column {
  padding-left: calc(var(--bs-gutter-x) * 0.5);
  padding-right: calc(var(--bs-gutter-x) * 0.5);
}

.venue-address {
  font-size: 0.8em;
  color: #687683;
  display: inline-block;
  white-space: pre-line;
}

.dummy {
  background-color: var(--bs-secondary-bg);
  display: block;
}
.dummy-blinker {
  animation: blinker 0.8s linear infinite;
}

@keyframes blinker {
  50% {
    opacity: 0.25;
  }
}

.dummy-provider {
  height: 9.5rem;
  width: 100%;
}

.venue-name-dummy {
  height: 2rem;
  width: 80%;
}

.venue-address-dummy {
  margin: 1rem 0;
  height: 3rem;
  width: 40%;
}

.dummy-actions {
  margin-top: 1rem;
  height: 2rem;
  width: 80%;
}

.highlighted {
  background-color: var(--bs-light-bg-subtle);
}

.venue-img {
  height: 70px;
  width: 100%;
  object-fit: cover;
}

.dummy-image {
  height: 70px;
  width: 100%;
  background-color: #aaa;
}

.request-status {
  font-size: 0.9rem;
}

.image-column-provider {
  padding: 0 0.5rem;
}

.provider-logo {
  background-repeat: no-repeat;
  background-size: contain;
  display: block;
  margin: 0.25rem 0 0;
  width: 60px;
  height: 32px;
}

.foursquare-logo {
  height: 10px;
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
