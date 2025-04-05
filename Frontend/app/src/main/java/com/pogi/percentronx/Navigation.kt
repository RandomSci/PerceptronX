package com.pogi.percentronx

import android.util.Log
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.google.accompanist.navigation.animation.composable
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

data class BottomNavItem(
    val route: String,
    val title: String,
    val icon: ImageVector
)

val bottomNavItems = listOf(
    BottomNavItem("main", "Home", Icons.Filled.Home),
    BottomNavItem("dashboard", "Dashboard", Icons.Filled.Settings),
    BottomNavItem("activity", "Activity", Icons.Filled.List),
    BottomNavItem("profile", "Profile", Icons.Filled.Person)
)

@Composable
fun MainScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            "Home Screen",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(16.dp))
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "Welcome to PerceptronX",
                    style = MaterialTheme.typography.titleLarge
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Navigate using the bottom bar",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
fun Activity() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            "Activity Screen",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.tertiary
        )
        Spacer(modifier = Modifier.height(20.dp))
        Card(
            modifier = Modifier
                .fillMaxWidth(0.8f)
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("Your recent activities will appear here", style = MaterialTheme.typography.bodyLarge)

                Text("SAMPLE TEXT")
            }
        }
    }
}

@Composable
fun Dashboard() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            "Dashboard Screen",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.secondary
        )
        Spacer(modifier = Modifier.height(20.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Card(
                modifier = Modifier
                    .weight(1f)
                    .padding(8.dp)
                    .height(100.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.secondaryContainer
                )
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Stats", style = MaterialTheme.typography.titleMedium)
                }
            }
            Card(
                modifier = Modifier
                    .weight(1f)
                    .padding(8.dp)
                    .height(100.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.tertiaryContainer
                )
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Reports", style = MaterialTheme.typography.titleMedium)
                }
            }
        }
    }
}

@Composable
fun Profile() {
    var status by remember { mutableStateOf<String?>("valid") }

    LaunchedEffect(key1 = Unit) {
        retrofitClient.instance.getStatus().enqueue(object : Callback<Status> {
            override fun onResponse(call: Call<Status>, response: Response<Status>) {
                if (response.isSuccessful) {
                    status = response.body()?.status
                    Log.d("API", "Status received: $status")
                } else {
                    Log.e("API", "Error: ${response.errorBody()?.string()}")
                }
            }

            override fun onFailure(call: Call<Status>, t: Throwable) {
                Log.e("API", "Failure: ${t.message}")
            }
        })
    }

    if (status == "valid") {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                "Profile Screen",
                style = MaterialTheme.typography.headlineLarge,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(20.dp))
            Surface(
                modifier = Modifier.size(120.dp),
                shape = MaterialTheme.shapes.extraLarge,
                color = MaterialTheme.colorScheme.primaryContainer
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Filled.Person,
                        contentDescription = "Profile",
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
            Spacer(modifier = Modifier.height(20.dp))
            Text(
                "User Name",
                style = MaterialTheme.typography.titleLarge
            )
            Text(
                "user@example.com",
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
    else {
        var username by remember { mutableStateOf("") }
        var gmail by remember { mutableStateOf("") }
        var username2 by remember { mutableStateOf("") }
        var password by remember { mutableStateOf("") }
        var password2 by remember { mutableStateOf("") }
        var statusMessage by remember { mutableStateOf("") }
        var statusMessage2 by remember { mutableStateOf("") }

        Column(
            Modifier
                .background(Color(1))
                .fillMaxSize()
                .padding(10.dp)
        ) {
            TextField(
                value = username,
                onValueChange = { username = it },
                label = { Text("Username") }
            )

            TextField(
                value = gmail,
                onValueChange = { gmail = it },
                label = { Text("Gmail") }
            )

            TextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("Password") },
                visualTransformation = PasswordVisualTransformation()
            )

            Button(onClick = {
                val call = retrofitClient.instance.registerUser(Register(username, gmail, password))
                call.enqueue(object : Callback<Status> {
                    override fun onResponse(call: Call<Status>, response: Response<Status>) {
                        statusMessage = if (response.isSuccessful) {
                            "Registered successfully!"
                        } else {
                            "Registration failed."
                        }
                    }

                    override fun onFailure(call: Call<Status>, t: Throwable) {
                        statusMessage = "Error: ${t.message}"
                    }
                })
            }) {
                Text("Register")
            }

            if (statusMessage.isNotEmpty()) {
                Text(statusMessage, color = Color.Green)
            }


            Text(text = "Log in")
            TextField(
                value = username2,
                onValueChange = {username2 = it},
                label = {Text("Username")}
            )
            TextField(
                value = password2,
                onValueChange = {password2 = it},
                label = {Text("Password")},
                visualTransformation = PasswordVisualTransformation()
            )
            Button(onClick = {
                val call = retrofitClient.instance.loginUser(Login(username, password))
                call.enqueue(object : Callback<Status> {
                    override fun onResponse(call: Call<Status>, response: Response<Status>) {
                        statusMessage2 = if (response.isSuccessful) {
                            "Logged in successfully!"
                        } else {
                            "Log in failed."
                        }
                    }

                    override fun onFailure(call: Call<Status>, t: Throwable) {
                        statusMessage2 = "Error: ${t.message}"
                    }

                })
            }) {
                Text("Login")
            }
            if (statusMessage2.isNotEmpty()) {
                Text(statusMessage2, color = Color.Green)
            }
        }
    }
}

@Composable
fun BottomNavigationBar(navController: NavController) {
    NavigationBar(
        modifier = Modifier.fillMaxWidth(),
        containerColor = MaterialTheme.colorScheme.surfaceVariant,
        tonalElevation = 8.dp
    ) {
        val navBackStackEntry by navController.currentBackStackEntryAsState()
        val currentDestination = navBackStackEntry?.destination

        bottomNavItems.forEach { item ->
            val selected = currentDestination?.hierarchy?.any { it.route == item.route } == true

            NavigationBarItem(
                icon = {
                    Icon(
                        imageVector = item.icon,
                        contentDescription = item.title
                    )
                },
                label = { Text(item.title) },
                selected = selected,
                onClick = {
                    navController.navigate(item.route) {
                        popUpTo(navController.graph.findStartDestination().id) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = MaterialTheme.colorScheme.primary,
                    selectedTextColor = MaterialTheme.colorScheme.primary,
                    indicatorColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    }
}

@Suppress("DEPRECATION")
@OptIn(ExperimentalAnimationApi::class)
@Composable
fun NavigationGraph() {
    val navController = rememberNavController()
    var status by remember { mutableStateOf<String?>("valid") }

    LaunchedEffect(key1 = Unit) {
        retrofitClient.instance.getStatus().enqueue(object : Callback<Status> {
            override fun onResponse(call: Call<Status>, response: Response<Status>) {
                if (response.isSuccessful) {
                    status = response.body()?.status
                    Log.d("API", "Status received: $status")
                } else {
                    Log.e("API", "Error: ${response.errorBody()?.string()}")
                }
            }

            override fun onFailure(call: Call<Status>, t: Throwable) {
                Log.e("API", "Failure: ${t.message}")
            }
        })
    }

    Scaffold(
        bottomBar = { BottomNavigationBar(navController) }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            NavHost(
                navController = navController,
                startDestination = if(status == "valid") "main" else "profile"
            ) {
                composable(
                    "main",
                    enterTransition = {
                        slideInHorizontally(initialOffsetX = { -it }) + fadeIn()
                    },
                    exitTransition = {
                        slideOutHorizontally(targetOffsetX = { -it }) + fadeOut()
                    }
                ) {
                    MainScreen()
                }
                composable(
                    "dashboard",
                    enterTransition = {
                        slideInHorizontally(initialOffsetX = { it }) + fadeIn()
                    },
                    exitTransition = {
                        slideOutHorizontally(targetOffsetX = { it }) + fadeOut()
                    }
                ) {
                    Dashboard()
                }
                composable(
                    "activity",
                    enterTransition = {
                        slideInHorizontally(initialOffsetX = { it }) + fadeIn()
                    },
                    exitTransition = {
                        slideOutHorizontally(targetOffsetX = { it }) + fadeOut()
                    }
                ) {
                    Activity()
                }
                composable(
                    "profile",
                    enterTransition = {
                        slideInHorizontally(initialOffsetX = { it }) + fadeIn()
                    },
                    exitTransition = {
                        slideOutHorizontally(targetOffsetX = { it }) + fadeOut()
                    }
                ) {
                    Profile()
                }
            }
        }
    }
}

