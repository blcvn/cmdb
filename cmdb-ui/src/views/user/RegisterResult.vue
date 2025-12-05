<template>
  <result
    :isSuccess="true"
    :content="false"
    :title="email"
    :description="description">

    <template slot="action">
      <a-button size="large" type="primary">Open Email</a-button>
      <a-button size="large" style="margin-left: 8px" @click="goHomeHandle">Back to Home</a-button>
    </template>

  </result>
</template>

<script>
import { Result } from '@/components'

export default {
  name: 'RegisterResult',
  components: {
    Result
  },
  data () {
    return {
      description: 'An activation email has been sent to your mailbox and is valid for 24 hours. Please check your email and click the link to activate your account.',
      form: {}
    }
  },
  computed: {
    email () {
      const v = this.form && this.form.email || 'xxx'
      const title = `Your account: ${v} registered successfully`
      return title
    }
  },
  created () {
    this.form = this.$route.params
  },
  methods: {
    goHomeHandle () {
      this.$router.push({ name: 'login' })
    }
  }
}
</script>

<style scoped>

</style>
