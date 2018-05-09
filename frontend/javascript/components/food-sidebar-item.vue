<template>
  <div class="sidebar-item" :id="'sidebar-' + itemId">
    <div class="sidebar-item-inner" :class="{requested: hasRequest, highlighted: data.sidebarHighlight}">
      <h5>
        {{ data.name }}
      </h5>
      <div class="container-fluid">
        <div class="row ">
          <div class="col-6">
            <p>
              <a :href="data.url" target="_blank" rel="noopener">
                <img :src="data.image" alt="Yelp venue image" class="venue-img img-fluid"/>
              </a>
            </p>
          </div>
          <div class="col-6 food-popup-info">
            <p>{{ data.address }}</p>
            <div class="col-12">
              <a :href="data.url" class="provider-logo" target="_blank" rel="noopener"></a>
            </div>
          </div>
        </div>
        <div class="row">
          <template v-if="hasRequest">
            <div class="col-6">
              <p>
                <small>
                  Anfrage zum Kontrollbericht wurde am {{ requestDate }} gestellt und {{ requestStatus }}.
                </small>
              </p>
            </div>
            <div class="col-6">
              <a class="btn btn-success request-button" :href="data.request_url" target="_blank">
                zur Anfrage
              </a>
            </div>
          </template>
          <template v-else>
            <div class="col-6">
              <p>
                <small>
                  Kontrollbericht kann angefragt werden.
                </small>
              </p>
            </div>
            <div class="col-6">
              <a class="btn btn-primary request-button" :href="requestUrl"  target="_blank">Jetzt anfragen!</a>
            </div>
          </template>
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
    }
  }
}
</script>

<style lang="scss" scoped>

.sidebar-item {
  padding: 80px 0.5rem 0.25rem;
  margin-top: -80px;
  width: 100%;

  small {
    line-height: 1.1;
    display: inline-block;
  }
}

.sidebar-item-inner {
  padding: 0.5rem;
}

.requested {
  background-color: #eee;
}

.highlighted {
  background-color: #fffbbf;
}

.venue-img {
  height: 120px;
  width: 100%;
  object-fit: cover;
}

.request-button {
  color: #fff !important;
  white-space: normal !important;
  display: block;
}



.provider-logo {
  background-image: url('/static/food/images/yelp_logo.png');
  background-repeat: no-repeat;
  background-size: contain;
  display: inline-block;
  width: 80px;
  height: 40px;
  // margin: 1rem 2rem;
  float: right;
}

</style>
