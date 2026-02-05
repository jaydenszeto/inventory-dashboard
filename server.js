const express = require("express");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.static("public"));
app.use(express.json());

// In-memory inventory storage
let inventory = [
  {
    id: 1,
    name: "Arduino Kit",
    quantity: 5,
    category: "Hardware",
    status: "Available",
  },
  {
    id: 2,
    name: "Figma License",
    quantity: 20,
    category: "Software",
    status: "Available",
  },
  {
    id: 3,
    name: "Wireless Mouse",
    quantity: 25,
    category: "Electronics",
    status: "Available",
  },
];
let nextId = 4;

// GET all inventory items
app.get("/api/inventory", (req, res) => {
  res.json(inventory);
});

// POST new inventory item
app.post("/api/inventory", (req, res) => {
  const { name, quantity, category, status } = req.body;

  if (!name || quantity == null || !category || !status) {
    return res
      .status(400)
      .json({ error: "name, quantity, category, and status are required." });
  }

  const newItem = {
    id: nextId++,
    name,
    quantity: parseInt(quantity),
    category,
    status,
  };

  inventory.push(newItem);
  res.status(201).json(newItem);
});

// PUT update inventory item
app.put("/api/inventory/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const { name, quantity, category, status } = req.body;

  const itemIndex = inventory.findIndex((item) => item.id === id);

  if (itemIndex === -1) {
    return res.status(404).json({ error: "Item not found." });
  }

  inventory[itemIndex] = {
    ...inventory[itemIndex],
    ...(name && { name }),
    ...(quantity != null && { quantity: parseInt(quantity) }),
    ...(category && { category }),
    ...(status && { status }),
  };

  res.json(inventory[itemIndex]);
});

// DELETE inventory item
app.delete("/api/inventory/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const itemIndex = inventory.findIndex((item) => item.id === id);

  if (itemIndex === -1) {
    return res.status(404).json({ error: "Item not found." });
  }

  const deletedItem = inventory.splice(itemIndex, 1)[0];
  res.json({ message: "Item deleted successfully.", item: deletedItem });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
