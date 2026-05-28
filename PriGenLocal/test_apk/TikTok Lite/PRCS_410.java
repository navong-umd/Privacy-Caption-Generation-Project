/*Application Package Name: com.tiktok.lite.go
class PRCS_410 {
/**
X.4Kc;L(Landroid/net/wifi/WifiManager; Landroid/app/Activity; Lkotlin/jvm/functions/Function1;)Z
*/

    public static boolean L(android.net.wifi.WifiManager p8, android.app.Activity p9, kotlin.jvm.functions.Function1 p10)
    {
        android.app.Application v5 = p9.getApplication();
        X.7Z7 v4_1 = new X.7Z7();
        v4_1.element = X.4Kc.LB;
        X.4Kb v6_1 = new X.4Kb(v4_1);
        v4_1.element = new Y.ARunnableS0S0400000_1(p10, v4_1, v5, v6_1, 2);
        X.4Kc.L(v5, v6_1, new android.content.IntentFilter("android.net.wifi.STATE_CHANGE"));
        X.4Kc.L.postDelayed(((Runnable) v4_1.element), 30000);
        try {
            if (p8.setWifiEnabled(1)) {
                if (X.4Kc.LB()) {
                    ((Runnable) v4_1.element).run();
                }
                return 1;
            } else {
                return 0;
            }
        } catch (Exception) {
            return 0;
        }
    }

/**
X.4Kc;L(Landroid/app/Activity; Lkotlin/jvm/functions/Function1;)V
*/

    public static void L(android.app.Activity p4, kotlin.jvm.functions.Function1 p5)
    {
        android.net.wifi.WifiManager v3 = X.4Kc.LBL();
        Boolean v2 = Boolean.valueOf(0);
        if (v3 != null) {
            if (!X.4Kc.L()) {
                if (android.os.Build$VERSION.SDK_INT >= 29) {
                    if (X.4Kc.LB(p4, p5)) {
                        return;
                    } else {
                        if (X.4Kc.L(v3, p4, p5)) {
                            return;
                        }
                    }
                } else {
                    if ((X.4Kc.L(v3, p4, p5)) || (X.4Kc.LB(p4, p5))) {
                        return;
                    }
                }
                android.content.Intent v1_1 = p4.getApplication();
                v1_1.registerActivityLifecycleCallbacks(new X.4Ka(v1_1, p5));
                try {
                    X.4Kc.L(p4, new android.content.Intent("android.settings.WIRELESS_SETTINGS"), "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPmtd4vH0jV92xn0HfnXdxaD5lZV");
                    return;
                } catch (Exception) {
                    p5.invoke(v2);
                    return;
                }
            } else {
                p5.invoke(Boolean.valueOf(1));
                return;
            }
        } else {
            p5.invoke(v2);
            return;
        }
    }

/**
X.4RS;L()V
*/

    public final void L()
    {
        String v4_2 = ((String) this.LBL.get(this.L));
        X.5PY v0_2 = new X.5PY(this, v4_2, 6);
        android.app.Activity v11 = X.16G.LI.L();
        int v1_2 = Boolean.valueOf(0);
        if (v11 != null) {
            android.content.Intent v3_2 = v4_2.hashCode();
            if (v3_2 == 3649301) {
                if (v4_2.equals("wifi")) {
                    if ((v11.isDestroyed()) || (v11.isFinishing())) {
                        v0_2.invoke(v1_2);
                        return;
                    } else {
                        android.content.Intent v3_3 = new String[] {"android.permission.ACCESS_WIFI_STATE", "android.permission.CHANGE_WIFI_STATE"});
                        if (android.os.Build$VERSION.SDK_INT >= 29) {
                            X.5Pc v2_21 = X.5ue.L(v11, v3_3);
                            if (!((java.util.Collection) v2_21).isEmpty()) {
                                X.5Pc v2_22 = v2_21.iterator();
                                while (v2_22.hasNext()) {
                                    if (!((Boolean) v2_22.next()).booleanValue()) {
                                        X.5ue.L(v11, v3_3, new X.5Pc(v11, v0_2, 17));
                                        return;
                                    }
                                }
                            }
                        }
                        X.4Kc.L(v11, v0_2);
                        return;
                    }
                }
            } else {
                if (v3_2 == 1901043637) {
                    if (v4_2.equals("location")) {
                        if (!X.4KW.L()) {
                            if ((v11.isDestroyed()) || (v11.isFinishing())) {
                                v0_2.invoke(v1_2);
                                return;
                            } else {
                                android.content.Intent v3_4 = v11.getApplication();
                                v3_4.registerActivityLifecycleCallbacks(new X.4KV(v3_4, v0_2));
                                try {
                                    android.content.Intent v3_6 = new android.content.Intent("android.settings.LOCATION_SOURCE_SETTINGS");
                                    com.bytedance.helios.statichook.api.HeliosApiHook v6_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                    Object[] v12 = new Object[2];
                                    v12[0] = v3_6;
                                    v12[1] = Integer.valueOf(1);
                                    com.bytedance.helios.statichook.api.ExtraInfo v13_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/content/Intent;I)V", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPmtd4vH0jV92xn0HeLRch6i+1BX728nqA==");
                                } catch (Exception) {
                                    v0_2.invoke(v1_2);
                                    return;
                                }
                                if (!v6_1.preInvoke(11094, "android/app/Activity", "startActivityForResult", v11, v12, "void", v13_1).intercept) {
                                    v11.startActivityForResult(v3_6, 1);
                                    v6_1.postInvoke(0, 11094, "android/app/Activity", "startActivityForResult", v11, v12, v13_1, 1);
                                    return;
                                } else {
                                    v6_1.postInvoke(0, 11094, "android/app/Activity", "startActivityForResult", v11, v12, v13_1, 0);
                                    return;
                                }
                            }
                        } else {
                            v0_2.invoke(Boolean.valueOf(1));
                            return;
                        }
                    }
                } else {
                    if ((v3_2 == 1968882350) && (v4_2.equals("bluetooth"))) {
                        if ((v11.isDestroyed()) || (v11.isFinishing())) {
                            v0_2.invoke(v1_2);
                            return;
                        } else {
                            android.content.Intent v3_1 = new String[] {"android.permission.BLUETOOTH_ADMIN", "android.permission.BLUETOOTH_CONNECT", "android.permission.BLUETOOTH_SCAN", "android.permission.BLUETOOTH_ADVERTISE"});
                            if (android.os.Build$VERSION.SDK_INT >= 31) {
                                X.5Pc v2_10 = X.5ue.L(v11, v3_1);
                                if (!((java.util.Collection) v2_10).isEmpty()) {
                                    X.5Pc v2_11 = v2_10.iterator();
                                    while (v2_11.hasNext()) {
                                        if (!((Boolean) v2_11.next()).booleanValue()) {
                                            X.5ue.L(v11, v3_1, new X.5Pc(v11, v0_2, 16));
                                            return;
                                        }
                                    }
                                }
                            }
                            X.4KU.L(v11, v0_2);
                            return;
                        }
                    }
                }
            }
            v0_2.invoke(v1_2);
            return;
        } else {
            v0_2.invoke(v1_2);
            return;
        }
    }


}