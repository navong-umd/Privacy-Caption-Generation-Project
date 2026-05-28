/*Application Package Name: com.tiktok.lite.go
class PRCS_330 {
/**
com.appsflyer.internal.AFi1uSDK;com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_registerNetworkCallback(Landroid/net/ConnectivityManager; Landroid/net/NetworkRequest; Landroid/net/ConnectivityManager$NetworkCallback; Ljava/lang/String;)V
*/

    public static void com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_registerNetworkCallback(android.net.ConnectivityManager p17, android.net.NetworkRequest p18, android.net.ConnectivityManager$NetworkCallback p19, String p20)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v11 = new Object[2];
        v11[0] = p18;
        v11[1] = p19;
        com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", p20);
        if (!v5_1.preInvoke(85, "android/net/ConnectivityManager", "registerNetworkCallback", p17, v11, "void", v12_1).intercept) {
            p17.registerNetworkCallback(p18, p19);
            v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", p17, v11, v12_1, 1);
            return;
        } else {
            v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", p17, v11, v12_1, 0);
            return;
        }
    }

/**
com.appsflyer.internal.AFi1uSDK;<init>(Landroid/content/Context;)V
*/

    public AFi1uSDK(android.content.Context p11)
    {
        super(p11);
        super.valueOf = "unknown";
        Throwable v3_2 = new com.appsflyer.internal.AFi1uSDK$AFa1tSDK(super);
        try {
            String v2_1 = super.AFInAppEventType;
        } catch (Throwable v3_0) {
            com.appsflyer.internal.AFg1fSDK.e$default(com.appsflyer.AFLogger.INSTANCE, com.appsflyer.internal.AFg1aSDK.afInfoLog, "Error at attempt to register network callback with ConnectivityManager", v3_0, 1, 0, 0, 0, 96, 0);
            return;
        }
        if (v2_1 != null) {
            com.appsflyer.internal.AFi1uSDK.com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_registerNetworkCallback(v2_1, new android.net.NetworkRequest$Builder().build(), v3_2, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfeleyw==");
        }
        return;
    }

/**
com.appsflyer.internal.AFb1vSDK;init(Ljava/lang/String; Lcom/appsflyer/AppsFlyerConversionListener; Landroid/content/Context;)Lcom/appsflyer/AppsFlyerLib;
*/

    public final com.appsflyer.AppsFlyerLib init(String p12, com.appsflyer.AppsFlyerConversionListener p13, android.content.Context p14)
    {
        if (!this.w) {
            long v0_9;
            this.w = 1;
            this.AFInAppEventParameterName().i().AFLogger = p12;
            com.appsflyer.internal.AFb1mSDK.valueOf(p12);
            if (p14 != null) {
                v0_9 = 9;
            } else {
                v0_9 = 26;
            }
            if (v0_9 == 26) {
                com.appsflyer.AFLogger.INSTANCE.w(com.appsflyer.internal.AFg1aSDK.registerClient, "context is null, Google Install Referrer will be not initialized");
            } else {
                StringBuilder v1_20;
                StringBuilder v1_14 = (com.appsflyer.internal.AFb1vSDK.afLogForce + 17);
                com.appsflyer.internal.AFb1vSDK.AFPurchaseDetails = (v1_14 % 128);
                if ((v1_14 % 2) == 0) {
                    this.valueOf(p14);
                    v1_20 = com.appsflyer.internal.AFb1uSDK.AFInAppEventParameterName(p14);
                    if ((v1_20 instanceof Object)) {
                        StringBuilder v1_24;
                        this.v = v1_20;
                        this.AFInAppEventParameterName().afErrorLog().AFInAppEventParameterName();
                        this.AFInAppEventParameterName().AFLogger().values = System.currentTimeMillis();
                        byte[] v6_7 = this.AFInAppEventParameterName().afInfoLog();
                        v6_7.valueOf.execute(new com.appsflyer.internal.AFe1cSDK$2(v6_7, new com.appsflyer.internal.AFf1uSDK(this.AFInAppEventParameterName())));
                        com.appsflyer.internal.AFg1aSDK v5_17 = this.AFInAppEventParameterName().afLogForce();
                        if (android.os.Build$VERSION.SDK_INT < 31) {
                            v1_24 = new com.appsflyer.internal.AFi1ySDK(v5_17.AFKeystoreWrapper);
                        } else {
                            v1_24 = new com.appsflyer.internal.AFi1uSDK(v5_17.AFKeystoreWrapper);
                        }
                        v5_17.valueOf = v1_24;
                        this.AFInAppEventParameterName().getCurrency().values(new com.appsflyer.internal.-$$Lambda$AFb1vSDK$5(this));
                        this.AFInAppEventParameterName().registerClient().AFKeystoreWrapper(this.e());
                        com.appsflyer.internal.AFg1wSDK v7_1 = this.AFInAppEventParameterName().force();
                        StringBuilder v1_29 = new com.appsflyer.internal.-$$Lambda$AFb1vSDK$3(this);
                        long v0_75 = v7_1.valueOf(v1_29);
                        Runnable v9 = v7_1.AFInAppEventType(v0_75, v1_29);
                        v7_1.AFInAppEventParameterName(v0_75);
                        v7_1.AFInAppEventParameterName(new com.appsflyer.internal.AFi1eSDK(v7_1.AFInAppEventParameterName.AFInAppEventType(), v9));
                        v7_1.AFInAppEventParameterName(new com.appsflyer.internal.AFi1nSDK(v9, v7_1.AFInAppEventParameterName, new com.appsflyer.internal.AFi1oSDK()));
                        v7_1.AFInAppEventParameterName(new com.appsflyer.internal.AFi1bSDK(v9, v7_1.AFInAppEventParameterName));
                        v7_1.AFInAppEventParameterName(v9);
                        if (!v7_1.values()) {
                            byte[] v6_0 = v7_1.AFInAppEventParameterName;
                            StringBuilder v1_7 = v7_1.AFInAppEventParameterName.w().AFKeystoreWrapper.getPackageManager().queryIntentContentProviders(new android.content.Intent("com.appsflyer.referrer.INSTALL_PROVIDER"), 0);
                            if ((v1_7 != null) && (!v1_7.isEmpty())) {
                                com.appsflyer.internal.AFg1uSDK v8_1 = new java.util.ArrayList();
                                java.util.Iterator v10 = v1_7.iterator();
                                while (v10.hasNext()) {
                                    StringBuilder v1_17 = ((android.content.pm.ResolveInfo) v10.next()).providerInfo;
                                    if (v1_17 == null) {
                                        com.appsflyer.AFLogger.INSTANCE.w(com.appsflyer.internal.AFg1aSDK.afErrorLog, "com.appsflyer.referrer.INSTALL_PROVIDER Action is set for non ContentProvider component");
                                    } else {
                                        v8_1.add(new com.appsflyer.internal.AFi1iSDK(v1_17, v9, v6_0));
                                    }
                                }
                                if (!v8_1.isEmpty()) {
                                    v7_1.AFKeystoreWrapper.addAll(v8_1);
                                    StringBuilder v1_9 = new StringBuilder("Detected ");
                                    v1_9.append(v8_1.size());
                                    v1_9.append(" valid preinstall provider(s)");
                                    com.appsflyer.AFLogger.INSTANCE.d(com.appsflyer.internal.AFg1aSDK.afErrorLog, v1_9.toString());
                                }
                            }
                        }
                        com.appsflyer.internal.AFg1uSDK v8_2 = v7_1.AFKeystoreWrapper();
                        byte[] v6_2 = v8_2.length;
                        com.appsflyer.internal.AFg1aSDK v5_3 = 0;
                        while (v5_3 < v6_2) {
                            v8_2[v5_3].values(v7_1.AFInAppEventParameterName.w().AFKeystoreWrapper);
                            v5_3++;
                        }
                        com.appsflyer.internal.AFg1wSDK v7_0 = this.force.i();
                        byte[] v6_3 = this.AFInAppEventParameterName().AFInAppEventType();
                        v7_0.valueOf = System.currentTimeMillis();
                        com.appsflyer.internal.AFg1uSDK v8_3 = v7_0.AFInAppEventParameterName;
                        com.appsflyer.internal.AFg1aSDK v5_6 = new StringBuilder();
                        v5_6.append(com.appsflyer.internal.AFb1kSDK.valueOf(v6_3.valueOf, v6_3.AFKeystoreWrapper));
                        v5_6.append(v7_0.valueOf);
                        byte[] v6_4 = com.appsflyer.internal.AFb1lSDK.values(v5_6.toString());
                        long v0_33 = -1;
                        if ((v6_4 != null) && (v6_4.length > 0)) {
                            if (v6_4.length > 8) {
                                v6_4 = java.util.Arrays.copyOfRange(v6_4, 0, 8);
                            }
                            long v0_35 = java.nio.ByteBuffer.allocate(8);
                            v0_35.put(v6_4);
                            v0_35.flip();
                            v0_33 = v0_35.getLong();
                        }
                        v7_0.values = v8_3.AFKeystoreWrapper(v0_33, v7_0.AFKeystoreWrapper.AFKeystoreWrapper, new com.appsflyer.internal.AFg1wSDK$3(v7_0));
                        long v0_39;
                        com.appsflyer.internal.AFg1aSDK v5_11 = this.AFInAppEventParameterName().v();
                        StringBuilder v1_15 = new String[2];
                        v1_15[0] = p12;
                        if (p13 != null) {
                            v0_39 = "conversionDataListener";
                        } else {
                            v0_39 = "null";
                        }
                        v1_15[1] = v0_39;
                        v5_11.AFInAppEventParameterName("init", v1_15);
                        StringBuilder v1_16 = new Object[2];
                        v1_16[0] = "6.14.0";
                        v1_16[1] = com.appsflyer.internal.AFb1vSDK.values;
                        com.appsflyer.AFLogger.INSTANCE.force(com.appsflyer.internal.AFg1aSDK.afWarnLog, String.format("Initializing AppsFlyer SDK: (v%s.%s)", v1_16));
                        this.AFInAppEventType = p13;
                        return this;
                    }
                } else {
                    this.valueOf(p14);
                    v1_20 = com.appsflyer.internal.AFb1uSDK.AFInAppEventParameterName(p14);
                    if (v1_20 != null) {
                    }
                }
                com.appsflyer.internal.AFb1vSDK.afLogForce = ((com.appsflyer.internal.AFb1vSDK.AFPurchaseDetails + 19) % 128);
                return this;
            }
        } else {
            return this;
        }
    }


}