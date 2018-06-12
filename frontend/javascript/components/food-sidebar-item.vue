<template>
  <div class="sidebar-item" :id="'sidebar-' + itemId">
    <div class="sidebar-item-inner" :class="{requested: hasRequest, highlighted: isSelected}" @click="$emit('select', data)">
      <div class="container-fluid">
        <div class="row ">
          <div class="col-3 col-md-4 image-column">
            <a class="image-column-inner" :href="data.url" target="_blank" rel="noopener">
              <img v-if="data.image" :src="data.image" alt="Yelp venue image" class="venue-img img-fluid"/>
              <div v-else class="dummy-image"></div>
              <div class="image-column-provider">
                <div class="provider-logo"></div>
                <div :class="starClass" :title="starRating"></div>
                <small class="review-count">{{ data.review_count }} Beiträge</small>
              </div>
            </a>
          </div>
          <div class="col col-md-8 info-column">
            <h5 class="venue-name">
              {{ data.name }}
            </h5>
            <p class="venue-address">{{ data.address }}</p>
            <a v-if="!data.request_status" class="btn btn-primary" :href="requestUrl"  target="_blank">
              Hygienekontrolle anfragen&nbsp;&rarr;
            </a>
            <a  v-else class="to-request-button" :href="data.request_url" target="_blank">
              zur Anfrage&nbsp;&rarr;
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FoodItemMixin from '../lib/mixin'

export default {
  name: 'food-sidebar-item',
  mixins: [FoodItemMixin],
  props: {
    data: {
      type: Object
    },
    selectedFacilityId: {
      type: String
    },
    config: {
      type: Object
    }
  }
}
</script>

<style lang="scss" scoped>

@import "../../styles/yelp_stars";

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

@media screen and (min-width: 768px){
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
  cursor: pointer;
}

@media screen and (min-width: 768px){
  .image-column {
    padding: 0 5px 0 5px;
  }
}


@media screen and (min-width: 768px){
  .map-container {
    height: 80vh;
  }
  .sidebar {
    height: 80vh;
    overflow-y: scroll;
  }
}

.image-column-inner {
  display: block;
  background-color: #eee;
  padding: 0;
}

.image-column-inner:hover {
  text-decoration: none;
}

.info-column {
  padding-left: 15px;
  padding-right: 0;
}

.venue-address {
  font-size: 0.8em;
  color: #687683;
  display: inline-block;
  white-space: pre-line;
}

.requested {

}

.highlighted {
  background-color: #fffbbf;
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

.to-request-button {
  display: block;
  color: #28a745;
}

.image-column-provider {
  padding: 0 0.5rem;
}

.provider-logo {
  background-image: url('/static/food/images/yelp_logo.png');
  background-repeat: no-repeat;
  background-size: contain;
  display: block;
  margin: 0.25rem 0 0;
  width: 60px;
  height: 32px;
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
