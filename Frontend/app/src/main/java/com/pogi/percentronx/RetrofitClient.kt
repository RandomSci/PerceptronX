package com.pogi.percentronx

import com.google.gson.GsonBuilder
import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object retrofitClient {
    private val cookieJar = object : CookieJar {
        private val cookieStore = HashMap<String, List<Cookie>>()

        override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
            cookieStore[url.host] = cookies
        }

        override fun loadForRequest(url: HttpUrl): List<Cookie> {
            return cookieStore[url.host] ?: ArrayList()
        }
    }

    private val gson = GsonBuilder()
        .setLenient()
        .create()

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val client = OkHttpClient.Builder()
        .cookieJar(cookieJar)
        .addInterceptor(loggingInterceptor)
        .build()

    val instance: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl("http://192.168.1.14:8000/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(ApiService::class.java)
    }
}