using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

[System.Serializable]
class MyCar
{
    public int id;
    public int x;
    public int y;
    public int o;

    override public string ToString()
    {
        return "ID: " + id + ", X: " + x + ", Y: " + y + ", O: " + o;
    }
}

[System.Serializable]
class MyLight
{
    public int id;
    public int state;

    override public string ToString()
    {
        return "ID: " + id +  "S: " + state;
    }
}

[System.Serializable]
class AgentCollection
{
    public MyCar[] cars;
    public MyLight[] tlights;
}

public class Controlador : MonoBehaviour
{
    string simulationURL;
    private float waitTime = 0.5f;
    private float timer = 0.0f;

    public GameObject[] autos;
    public GameObject[] semaforos;

    public Material[] material;

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(ConnectToMesa());
        StartCoroutine(UpdatePositions());
    }

    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/games", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log(www.error);
            }
            else
            {
                simulationURL = www.GetResponseHeader("Location");
                Debug.Log("Connected to simulation through Web API");
                Debug.Log(simulationURL);
            }
        }
    }
    float getRotation(int orientacion)
    {
        if(orientacion == 1)
        {
            return -90;
        }else if(orientacion == 2)
        {
            return 90;
        }else if(orientacion == 3)
        {
            return 0;
        }
        else
        {
            return -180;
        }
    }

        IEnumerator UpdatePositions()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(simulationURL))
        {
            if (simulationURL != null)
            {
                // Request and wait for the desired page.
                yield return www.SendWebRequest();

                Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");
                AgentCollection agents = JsonUtility.FromJson<AgentCollection>(www.downloadHandler.text);

                foreach (MyCar car in agents.cars)
                {
                    autos[car.id-1].transform.position = new Vector3((car.x * 10) + 5, 0, (car.y * 10) + 5);
                    autos[car.id-1].transform.rotation= Quaternion.Euler(0, getRotation(car.o), 0);
                } 

                foreach (MyLight tlight in agents.tlights)
                {
                    Renderer rendRojo = semaforos[tlight.id - 16].transform.Find("redLight").gameObject.GetComponent<Renderer>();
                    Renderer rendAmarillo = semaforos[tlight.id - 16].transform.Find("yellowLight").gameObject.GetComponent<Renderer>();
                    Renderer rendVerde = semaforos[tlight.id - 16].transform.Find("greenLight").gameObject.GetComponent<Renderer>();
                    rendRojo.enabled = true;
                    rendAmarillo.enabled = true;
                    rendVerde.enabled = true;

                    if (tlight.state == 0) //Rojo
                    {
                        rendRojo.sharedMaterial = material[0];
                        rendAmarillo.sharedMaterial = material[3];
                        rendVerde.sharedMaterial = material[3];
                    }
                    else if (tlight.state == 1) //Amarillo
                    {
                        rendRojo.sharedMaterial = material[3];
                        rendAmarillo.sharedMaterial = material[1];
                        rendVerde.sharedMaterial = material[3];
                    }
                    else if (tlight.state == 2) //Verde
                    {
                        rendRojo.sharedMaterial = material[3];
                        rendAmarillo.sharedMaterial = material[3];
                        rendVerde.sharedMaterial = material[2];
                    }
                    else //Todo apagado
                    {
                        rendRojo.sharedMaterial = material[3];
                        rendAmarillo.sharedMaterial = material[3];
                        rendVerde.sharedMaterial = material[3];
                    }
                }              
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer > waitTime)
        {
            StartCoroutine(UpdatePositions());
            timer = timer - waitTime;
        }
    }
}
